import json
import logging
import random

from pathlib import Path

import numpy as np

from app.ml.complexity_classifier import nlp

logger = logging.getLogger(__name__)

LEXICON_PATH = Path(__file__).resolve().parents[1] / "data" / "lexicon" / "output.json"

# ============================================================
# CARREGAMENTO DO DICIONÁRIO
# ============================================================


def load_lexicon() -> dict:
    if not LEXICON_PATH.is_file():
        logger.warning(
            "Dicionário lexical não encontrado: %s",
            LEXICON_PATH,
        )
        return {}

    try:
        with LEXICON_PATH.open(encoding="utf-8") as file:
            lexicon = json.load(file)

        if not isinstance(lexicon, dict):
            raise ValueError("Formato inválido no dicionário.")

        return lexicon

    except (OSError, json.JSONDecodeError, ValueError):
        logger.exception("Erro ao carregar o dicionário lexical.")
        return {}


LEXICON = load_lexicon()


POS_TO_CATEGORY = {
    "NOUN": "noun",
    "ADJ": "adjective",
    "VERB": "verb",
    "ADV": "adverb",
}


# ============================================================
# VETORES SEMÂNTICOS
# ============================================================

_VECTOR_CACHE: dict[str, np.ndarray | None] = {}


def get_word_vector(word: str) -> np.ndarray | None:
    """
    Retorna o vetor estático de uma palavra no vocabulário spaCy.

    O modelo precisa possuir vetores semânticos, como
    pt_core_news_lg.
    """

    key = word.casefold()

    if key in _VECTOR_CACHE:
        return _VECTOR_CACHE[key]

    lexeme = nlp.vocab[key]

    if not lexeme.has_vector or lexeme.vector_norm == 0:
        _VECTOR_CACHE[key] = None
        return None

    vector = np.asarray(lexeme.vector, dtype=np.float32)

    _VECTOR_CACHE[key] = vector

    return vector


def cosine_similarity(
    vector_a: np.ndarray | None,
    vector_b: np.ndarray | None,
) -> float | None:
    """
    Calcula a similaridade de cosseno entre dois vetores.
    """

    if vector_a is None or vector_b is None:
        return None

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    if norm_a == 0 or norm_b == 0:
        return None

    return float(np.dot(vector_a, vector_b) / (norm_a * norm_b))


def get_context_tokens(token, window: int = 4) -> list:
    """
    Obtém palavras relevantes próximas ao token, sem incluir
    a própria palavra que será substituída.

    A busca fica limitada à sentença atual.
    """

    doc = token.doc

    start = max(token.sent.start, token.i - window)
    end = min(token.sent.end, token.i + window + 1)

    relevant_pos = {
        "NOUN",
        "PROPN",
        "ADJ",
        "VERB",
        "ADV",
    }

    neighbors = []

    for neighbor in doc[start:end]:
        if neighbor.i == token.i:
            continue

        if (
            not neighbor.is_alpha
            or neighbor.is_stop
            or neighbor.pos_ not in relevant_pos
        ):
            continue

        if not neighbor.has_vector or neighbor.vector_norm == 0:
            continue

        distance = abs(neighbor.i - token.i)

        # Palavras próximas recebem mais peso.
        weight = 1.0 / distance

        neighbors.append((neighbor, weight))

    return neighbors


def contextual_similarity(
    candidate_vector: np.ndarray,
    context_tokens: list,
) -> float | None:
    """
    Mede a proximidade semântica do candidato em relação
    às palavras vizinhas do contexto.

    Não é uma medida direta de sinonímia ou antonímia.
    """

    if not context_tokens:
        return None

    weighted_sum = 0.0
    total_weight = 0.0

    for context_token, weight in context_tokens:
        similarity = cosine_similarity(
            candidate_vector,
            context_token.vector,
        )

        if similarity is None:
            continue

        weighted_sum += similarity * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return weighted_sum / total_weight


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================


def preserve_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()

    if original.istitle():
        return replacement[:1].upper() + replacement[1:]

    return replacement


def replace_spans(
    text: str,
    replacements: list[tuple[int, int, str]],
) -> str:
    """
    Aplica substituições da direita para a esquerda para
    preservar os offsets originais do texto.
    """

    for start, end, replacement in sorted(
        replacements,
        key=lambda item: item[0],
        reverse=True,
    ):
        text = text[:start] + replacement + text[end:]

    return text


def adapt_inflection(token, candidate: str) -> str:
    """
    Ajustes básicos de gênero e número para substantivos
    e adjetivos. Não cobre todas as irregularidades do português.
    """

    candidate = candidate.casefold()

    if token.pos_ not in {"NOUN", "ADJ"}:
        return preserve_case(token.text, candidate)

    genders = token.morph.get("Gender")
    numbers = token.morph.get("Number")

    if "Fem" in genders and candidate.endswith("o"):
        candidate = candidate[:-1] + "a"

    elif (
        "Masc" in genders
        and token.text.casefold().endswith("o")
        and candidate.endswith("a")
    ):
        candidate = candidate[:-1] + "o"

    if "Plur" in numbers and not candidate.endswith("s"):
        if candidate.endswith("m"):
            candidate = candidate[:-1] + "ns"

        elif candidate.endswith(("r", "z")):
            candidate += "es"

        elif candidate.endswith("al"):
            candidate = candidate[:-2] + "ais"

        elif candidate.endswith("el"):
            candidate = candidate[:-2] + "éis"

        elif candidate.endswith("ol"):
            candidate = candidate[:-2] + "óis"

        elif candidate.endswith("ul"):
            candidate = candidate[:-2] + "uis"

        elif candidate.endswith("il"):
            candidate = candidate[:-2] + "eis"

        elif candidate.endswith(("ção", "são", "xão")):
            candidate = candidate[:-2] + "ões"

        else:
            candidate += "s"

    return preserve_case(token.text, candidate)


# ============================================================
# TROCA DE PALAVRAS — SELEÇÃO POR SIMILARIDADE
# ============================================================


def candidates_for(token) -> list[tuple[str, str, str]]:
    """
    Retorna candidatos compatíveis com a categoria gramatical.

    Cada candidato contém:
        (forma_de_substituicao, relacao, forma_lexical)

    A forma lexical é usada para consultar os vetores,
    enquanto a forma de substituição pode estar flexionada.
    """

    category = POS_TO_CATEGORY.get(token.pos_)

    if category is None:
        return []

    if token.is_stop or not token.is_alpha or token.pos_ == "PROPN":
        return []

    # Verbos só são trocados quando estão no infinitivo.
    # Assim, evitamos substituir diretamente formas conjugadas.
    if token.pos_ == "VERB" and "Inf" not in token.morph.get("VerbForm"):
        return []

    entries = LEXICON.get(category, {})

    if not isinstance(entries, dict):
        return []

    possible_keys = list(
        dict.fromkeys(
            [
                token.text.casefold(),
                token.lemma_.casefold(),
            ]
        )
    )

    candidates = []
    seen = set()

    for key in possible_keys:
        entry = entries.get(key)

        if not isinstance(entry, dict):
            continue

        for relation in ("synonyms", "antonyms"):
            values = entry.get(relation, [])

            if not isinstance(values, list):
                continue

            for value in values:
                if not isinstance(value, str):
                    continue

                lexical_form = value.strip().casefold()

                if not lexical_form or not lexical_form.isalpha():
                    continue

                if lexical_form in possible_keys:
                    continue

                # Sem vetor, não há como fazer a seleção semântica.
                if get_word_vector(lexical_form) is None:
                    continue

                replacement = adapt_inflection(
                    token,
                    lexical_form,
                )

                identity = (replacement.casefold(), relation)

                if identity in seen:
                    continue

                seen.add(identity)

                candidates.append(
                    (
                        replacement,
                        relation,
                        lexical_form,
                    )
                )

    return candidates


def score_candidate(
    token,
    lexical_form: str,
    relation: str,
    context_tokens: list,
) -> float | None:
    """
    Pontua o candidato usando vetores semânticos.

    Sinônimos:
        combina a similaridade com a palavra original e
        a compatibilidade com o contexto.

    Antônimos:
        prioriza a compatibilidade contextual, pois a relação
        de antonímia já vem do dicionário.
    """

    candidate_vector = get_word_vector(lexical_form)

    if candidate_vector is None:
        return None

    target_vector = token.vector if token.has_vector and token.vector_norm > 0 else None

    word_similarity = cosine_similarity(
        target_vector,
        candidate_vector,
    )

    context_score = contextual_similarity(
        candidate_vector,
        context_tokens,
    )

    if relation == "synonyms":
        if context_score is None:
            return word_similarity

        if word_similarity is None:
            return context_score

        return 0.55 * context_score + 0.45 * word_similarity

    if relation == "antonyms":
        if context_score is None:
            return None

        if word_similarity is None:
            return context_score

        return 0.85 * context_score + 0.15 * word_similarity

    return None


def best_candidate_for(token) -> str | None:
    """
    Seleciona o candidato de maior pontuação semântica.

    O candidato final é escolhido de forma determinística
    para uma dada entrada e um dicionário fixo.
    """

    candidates = candidates_for(token)

    if not candidates:
        return None

    context_tokens = get_context_tokens(token)

    scored_candidates = []

    for replacement, relation, lexical_form in candidates:
        score = score_candidate(
            token,
            lexical_form,
            relation,
            context_tokens,
        )

        if score is None:
            continue

        scored_candidates.append((score, replacement, relation))

    if not scored_candidates:
        return None

    scored_candidates.sort(
        key=lambda item: (
            -item[0],
            item[1].casefold(),
            item[2],
        )
    )

    return scored_candidates[0][1]


def swap_words(text: str) -> str:
    """
    Substitui uma parte das palavras elegíveis.

    A escolha dos candidatos utiliza similaridade.
    A escolha de quais posições modificar continua aleatória.
    """

    doc = nlp(text)
    eligible = []

    for token in doc:
        replacement = best_candidate_for(token)

        if replacement is not None:
            eligible.append((token, replacement))

    if not eligible:
        return text

    random.shuffle(eligible)

    max_changes = min(
        5,
        max(1, round(len(eligible) * 0.15)),
    )

    replacements = []

    for token, replacement in eligible[:max_changes]:
        replacements.append(
            (
                token.idx,
                token.idx + len(token.text),
                replacement,
            )
        )

    return replace_spans(text, replacements)


# ============================================================
# TROCA DE GÊNERO
# ============================================================

GENDER_PAIRS = [
    ("menino", "menina"),
    ("homem", "mulher"),
    ("pai", "mãe"),
    ("filho", "filha"),
    ("irmão", "irmã"),
    ("marido", "esposa"),
    ("ator", "atriz"),
    ("cantor", "cantora"),
    ("professor", "professora"),
    ("aluno", "aluna"),
    ("autor", "autora"),
    ("escritor", "escritora"),
    ("diretor", "diretora"),
    ("médico", "médica"),
    ("advogado", "advogada"),
    ("pesquisador", "pesquisadora"),
    ("trabalhador", "trabalhadora"),
    ("amigo", "amiga"),
    ("vizinho", "vizinha"),
    ("brasileiro", "brasileira"),
    ("bonito", "bonita"),
    ("famoso", "famosa"),
    ("alto", "alta"),
    ("baixo", "baixa"),
    ("cansado", "cansada"),
    ("dedicado", "dedicada"),
    ("preparado", "preparada"),
    ("aprovado", "aprovada"),
    ("satisfeito", "satisfeita"),
    ("interessado", "interessada"),
    ("querido", "querida"),
    ("novo", "nova"),
    ("velho", "velha"),
    ("pequeno", "pequena"),
    ("primeiro", "primeira"),
    ("último", "última"),
]


def build_symmetric_map(
    pairs: list[tuple[str, str]],
) -> dict[str, str]:
    result = {}

    for masculine, feminine in pairs:
        result[masculine] = feminine
        result[feminine] = masculine

    return result


GENDER_MAP = build_symmetric_map(GENDER_PAIRS)

DETERMINER_PAIRS = [
    ("o", "a"),
    ("os", "as"),
    ("um", "uma"),
    ("uns", "umas"),
    ("este", "esta"),
    ("estes", "estas"),
    ("esse", "essa"),
    ("esses", "essas"),
    ("aquele", "aquela"),
    ("aqueles", "aquelas"),
    ("meu", "minha"),
    ("meus", "minhas"),
    ("teu", "tua"),
    ("teus", "tuas"),
    ("seu", "sua"),
    ("seus", "suas"),
    ("nosso", "nossa"),
    ("nossos", "nossas"),
]

DETERMINER_MAP = build_symmetric_map(DETERMINER_PAIRS)

CONTRACTION_PAIRS = [
    ("do", "da"),
    ("dos", "das"),
    ("no", "na"),
    ("nos", "nas"),
    ("pelo", "pela"),
    ("pelos", "pelas"),
]

CONTRACTION_MAP = build_symmetric_map(CONTRACTION_PAIRS)


def find_gender_replacement(token) -> str | None:
    """
    Procura uma forma de gênero oposto no mapa de pares.
    """

    replacement = GENDER_MAP.get(token.text.casefold())

    if replacement is not None:
        return preserve_case(token.text, replacement)

    return None


def adjective_is_related_to_noun(adjective, noun) -> bool:
    """
    Verifica se o adjetivo está relacionado ao substantivo.

    Considera:
    1. Adjetivos diretamente ligados ao substantivo:
    2. Adjetivos predicativos com o substantivo como sujeito:
    3. Estruturas em que o verbo ou auxiliar conecta o substantivo ao adjetivo.
    """

    # Caso 1: modificador direto.
    if adjective.head.i == noun.i:
        return True

    subject_dependencies = {
        "nsubj",
        "nsubjpass",
        "csubj",
        "csubjpass",
    }

    def is_subject(token) -> bool:
        base_dependency = token.dep_.split(":")[0]
        return base_dependency in subject_dependencies

    # Caso 2: o adjetivo é o núcleo do predicado.

    if any(child.i == noun.i and is_subject(child) for child in adjective.children):
        return True

    # Caso 3: o adjetivo depende de um verbo ou auxiliar.
    # Exemplo: o verbo conecta o sujeito ao predicativo.
    governor = adjective.head

    if governor.pos_ in {"VERB", "AUX"}:
        if any(child.i == noun.i and is_subject(child) for child in governor.children):
            return True

        # Considera também estruturas em que o substantivo
        # está ligado a outra classe por outro nível sintático.
        if noun.head.i == governor.i and is_subject(noun):
            return True

    return False


def swap_gender(text: str) -> str:
    """
    Troca o gênero de palavras conhecidas e ajusta alguns
    artigos e adjetivos associados.
    """

    doc = nlp(text)

    replacements_by_index = {}
    changed_nouns = []

    for token in doc:
        if token.pos_ not in {"NOUN", "PROPN"}:
            continue

        replacement = find_gender_replacement(token)

        if replacement is None:
            continue

        replacements_by_index[token.i] = (
            token.idx,
            token.idx + len(token.text),
            replacement,
        )

        changed_nouns.append(token)

    for noun in changed_nouns:
        for token in noun.sent:
            is_adjective = token.pos_ == "ADJ"

            # Alguns particípios com flexão de gênero, podem ser classificados como VERB pelo spaCy.
            is_gendered_participle = (
                token.pos_ in {"VERB", "AUX"}
                and "Part" in token.morph.get("VerbForm")
                and token.text.casefold() in GENDER_MAP
            )

            if not (is_adjective or is_gendered_participle):
                continue

            # Para particípios conhecidos, aceitamos a relação
            # com o substantivo alterado na mesma sentença.
            if not is_gendered_participle and not adjective_is_related_to_noun(
                token, noun
            ):
                continue

            replacement = find_gender_replacement(token)

            if replacement is None:
                continue

            replacements_by_index[token.i] = (
                token.idx,
                token.idx + len(token.text),
                replacement,
            )

    for noun in changed_nouns:
        for token in noun.sent:
            if token.i == noun.i:
                continue

            if token.head.i == noun.i and token.pos_ == "DET":
                replacement = DETERMINER_MAP.get(token.text.casefold())

                if replacement:
                    replacements_by_index[token.i] = (
                        token.idx,
                        token.idx + len(token.text),
                        preserve_case(token.text, replacement),
                    )

            contraction = CONTRACTION_MAP.get(token.text.casefold())

            if contraction is None:
                continue

            related_to_noun = token.head.i == noun.i or token.i + 1 == noun.i

            if related_to_noun:
                replacements_by_index[token.i] = (
                    token.idx,
                    token.idx + len(token.text),
                    preserve_case(token.text, contraction),
                )

    return replace_spans(
        text,
        list(replacements_by_index.values()),
    )


# ============================================================
# EXECUÇÃO DAS OPERAÇÕES
# ============================================================


def apply_text_operations(
    text: str,
    operations: dict,
) -> tuple[str, dict]:

    if operations.get("paraphrase", False):
        raise ValueError("A operação de paráfrase está indisponível no momento.")

    result = text

    applied = {
        "wordSwap": False,
        "genderSwap": False,
        "paraphrase": False,
    }

    # Primeiro troca o gênero para reconhecer os pares conhecidos
    # antes que a substituição lexical eventualmente os modifique.
    if operations.get("genderSwap", False):
        updated = swap_gender(result)
        applied["genderSwap"] = updated != result
        result = updated

    # Depois aplica sinônimos ou antônimos usando o texto atualizado.
    if operations.get("wordSwap", False):
        updated = swap_words(result)
        applied["wordSwap"] = updated != result
        result = updated

    return result, applied
