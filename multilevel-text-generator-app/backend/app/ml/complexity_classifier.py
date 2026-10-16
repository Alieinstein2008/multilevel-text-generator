import time
import joblib
import numpy as np
import pandas as pd
import spacy

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate,
)
from sklearn.pipeline import Pipeline

# ============================================================
# CONFIGURAÇÕES
# ============================================================

FOLDER = Path(__file__).resolve().parents[1] / "dataset_caed"

MODEL_PATH = Path(__file__).resolve().parent / "models" / "modelo_complexidade.joblib"
SPACY_MODEL = "pt_core_news_lg"

LABELS = {
    "1_Ensino_Fundamental_I": "EF1",
    "2_Ensino_Fundamental_II": "EF2",
    "3_Ensino_Medio": "EM",
    "4_Ensino_Superior": "ES",
}

CLASS_ORDER = list(LABELS.values())

# Número máximo de componentes latentes para o texto.
SVD_COMPONENTS = 100

# Limite de vocabulário TF-IDF.
TFIDF_MAX_FEATURES = 5000

# Número máximo de folds da validação cruzada.
CV_FOLDS = 5

CALCULAR_IMPORTANCIA = True

nlp = spacy.load(SPACY_MODEL)


# ============================================================
# VERBOS IRREGULARES
# ============================================================

IRREGULAR_VERBS = {
    "abster",
    "acudir",
    "adequar",
    "aderir",
    "adjazer",
    "advertir",
    "advir",
    "afazer",
    "aferir",
    "agredir",
    "ansiar",
    "antedar",
    "antepor",
    "antever",
    "apor",
    "aprazer",
    "apropinquar",
    "aspergir",
    "assentir",
    "ater",
    "atrair",
    "atribuir",
    "auferir",
    "autodestruir",
    "avir",
    "bem-dizer",
    "bem-fazer",
    "bem-querer",
    "bendizer",
    "benfazer",
    "benquerer",
    "buir",
    "bulir",
    "caber",
    "cair",
    "cerzir",
    "circumpor",
    "circunver",
    "cobrir",
    "compelir",
    "competir",
    "compor",
    "comprazer",
    "concernir",
    "concluir",
    "condizer",
    "conferir",
    "confugir",
    "conseguir",
    "consentir",
    "construir",
    "consumir",
    "conter",
    "contradizer",
    "contrafazer",
    "contrair",
    "contrapor",
    "contrapropor",
    "contravir",
    "convergir",
    "convir",
    "crer",
    "cuspir",
    "dar",
    "decompor",
    "deferir",
    "delinquir",
    "denegrir",
    "depor",
    "desafazer",
    "desaguar",
    "desapor",
    "desaprazer",
    "desavir",
    "descaber",
    "descobrir",
    "descompor",
    "descomprazer",
    "desconstruir",
    "desconvir",
    "descrer",
    "desdar",
    "desdizer",
    "desimpedir",
    "desimpor",
    "deslinguar",
    "desmedir",
    "desmentir",
    "desmobiliar",
    "despedir",
    "despir",
    "despolir",
    "despor",
    "desprazer",
    "desprecaver",
    "desprover",
    "desquerer",
    "dessaber",
    "destruir",
    "desvaler",
    "desver",
    "deter",
    "devir",
    "diferir",
    "digerir",
    "disferir",
    "disperder",
    "dispor",
    "distrair",
    "divergir",
    "divertir",
    "dizer",
    "dormir",
    "embair",
    "emergir",
    "encobrir",
    "engolir",
    "entredizer",
    "entrefazer",
    "entreouvir",
    "entrepor",
    "entrequerer",
    "entrever",
    "entrevir",
    "entupir",
    "enxaguar",
    "enxerir",
    "equivaler",
    "escapulir",
    "esfazer",
    "estar",
    "estrear",
    "esvair",
    "expedir",
    "expelir",
    "expor",
    "extrapor",
    "fazer",
    "ferir",
    "flectir",
    "fletir",
    "fotocompor",
    "fraguar",
    "frigir",
    "fugir",
    "gelifazer",
    "gerir",
    "haver",
    "idear",
    "imergir",
    "impedir",
    "impelir",
    "impor",
    "incendiar",
    "indeferir",
    "indispor",
    "inferir",
    "influir",
    "ingerir",
    "insatisfazer",
    "inserir",
    "interdizer",
    "intermediar",
    "interpor",
    "interver",
    "intervir",
    "investir",
    "ir",
    "jazer",
    "justapor",
    "ler",
    "liquefazer",
    "maisquerer",
    "maldispor",
    "maldizer",
    "malfazer",
    "malinguar",
    "malparir",
    "malquerer",
    "manter",
    "mediar",
    "medir",
    "mentir",
    "minguar",
    "obter",
    "obvir",
    "odiar",
    "opor",
    "ouvir",
    "parir",
    "pedir",
    "perder",
    "perfazer",
    "perseguir",
    "persentir",
    "pleitear",
    "poder",
    "poer",
    "polir",
    "pospor",
    "pôr",
    "prazer",
    "predispor",
    "predizer",
    "preferir",
    "prepor",
    "pressentir",
    "pressupor",
    "preterir",
    "prevenir",
    "prever",
    "proferir",
    "progredir",
    "propor",
    "prosseguir",
    "prossupor",
    "prover",
    "provir",
    "pruir",
    "puir",
    "putrefazer",
    "querer",
    "raer",
    "rarefazer",
    "readequar",
    "reaver",
    "reavir",
    "recobrir",
    "recompor",
    "reconvir",
    "redar",
    "redispor",
    "redizer",
    "reexpedir",
    "reexpor",
    "refazer",
    "referir",
    "refletir",
    "refugir",
    "regredir",
    "reimpor",
    "reindispor",
    "reinserir",
    "reler",
    "remediar",
    "remedir",
    "reobter",
    "reouvir",
    "repedir",
    "repelir",
    "repetir",
    "repor",
    "repropor",
    "requerer",
    "resfolegar",
    "ressentir",
    "reter",
    "retrair",
    "retranspor",
    "rever",
    "revestir",
    "revir",
    "rir",
    "ruir",
    "saber",
    "sacudir",
    "sair",
    "santiguar",
    "satisfazer",
    "seguir",
    "sentir",
    "ser",
    "servir",
    "sobpor",
    "sobre-expor",
    "sobreexpor",
    "sobrepor",
    "sobrestar",
    "sobrevir",
    "sorrir",
    "sortear",
    "sortir",
    "sotopor",
    "subir",
    "submergir",
    "subpor",
    "subsumir",
    "subtrair",
    "sugerir",
    "sumir",
    "superexpor",
    "superimpor",
    "superpor",
    "supor",
    "suster",
    "telever",
    "ter",
    "torrefazer",
    "tossir",
    "trair",
    "transfazer",
    "transferir",
    "transfugir",
    "transgredir",
    "transpor",
    "traspor",
    "trazer",
    "treler",
    "tresler",
    "trespor",
    "tumefazer",
    "valer",
    "ver",
    "vestir",
    "vir",
}

# ============================================================
# CARACTERÍSTICAS LINGUÍSTICAS
# ============================================================

VOWELS = set("aeiouáéíóúàâêôãõ")
CONSONANTS = set("bcdfghjklmnpqrstvwyxz")

ACCENTED_CHARS = set("áéíóúâêôãõàçÁÉÍÓÚÂÊÔÃÕÀÇ")

COMPLEX_PUNCT = {
    ";",
    ":",
    "—",
    "(",
    ")",
    "[",
    "]",
}


SPACY_FEATURE_NAMES = [
    "n_tokens",
    "n_sents",
    "sent_media",
    "palavra_media",
    "var_palavra",
    "ttr",
    "ttr_nominal",
    "ttr_verbal",
    "pct_noun",
    "pct_verb",
    "pct_adj",
    "pct_adp",
    "pct_cconj",
    "pct_sconj",
    "pct_pron",
    "pct_adv",
    "prof_media",
    "prof_max",
    "pct_modificadores",
    "tem_passiva",
    "pct_stop",
    "pct_passado",
    "pct_subjuntivo",
    "pct_pal_longas",
    "pct_propn",
    "canon_media",
    "pct_fully_canonical",
    "var_canon",
    "pct_pontuacao_complexa",
    "pct_tokens_acentuada",
    "pct_verbos_irregulares",
]


def canonicity_score(text: str) -> float:
    """
    Calcula uma medida heurística baseada em pares de caracteres
    consoante-vogal em posições alternadas.

    Observação: esta medida não representa, isoladamente,
    uma medida linguística validada de canonicidade.
    """
    text = text.lower().strip()

    if not text:
        return 0.0

    cv_count = 0

    for i in range(0, len(text), 2):
        if text[i] in CONSONANTS:
            if i + 1 < len(text) and text[i + 1] in VOWELS:
                cv_count += 1

    total_pairs = (len(text) + 1) // 2

    return cv_count / total_pairs if total_pairs > 0 else 0.0


def extract_features(doc) -> list:
    """
    Extrai 31 características linguísticas de um documento spaCy.
    """

    tokens = [t for t in doc if not t.is_space]
    sents = list(doc.sents)

    n = len(tokens)

    if n == 0:
        return [0.0] * len(SPACY_FEATURE_NAMES)

    # --------------------------------------------------------
    # Lemas e riqueza lexical
    # --------------------------------------------------------

    lemmas = [t.lemma_.lower() for t in tokens]
    unique_lemmas = set(lemmas)

    pos_counts = {}

    for token in tokens:
        pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1

    n_verbs = pos_counts.get("VERB", 0)

    # --------------------------------------------------------
    # Profundidade sintática
    # --------------------------------------------------------

    dependency_depths = []

    for token in tokens:
        current = token
        depth = 0

        while current.head.i != current.i:
            depth += 1
            current = current.head

        dependency_depths.append(depth)

    # --------------------------------------------------------
    # Comprimento das sentenças
    # --------------------------------------------------------

    sent_lengths = [sum(1 for token in sent if not token.is_space) for sent in sents]

    # --------------------------------------------------------
    # Voz passiva
    # --------------------------------------------------------

    has_passive = any(
        token.dep_ == "agent"
        or (token.pos_ == "VERB" and "Pass" in token.morph.get("Voice"))
        for token in tokens
    )

    # --------------------------------------------------------
    # Canonicidade heurística
    # --------------------------------------------------------

    canon_scores = [canonicity_score(token.text) for token in tokens]

    pct_fully_canonical = sum(score == 1.0 for score in canon_scores) / n

    # --------------------------------------------------------
    # Pontuação
    # --------------------------------------------------------

    punct_tokens = [token for token in tokens if token.is_punct]

    n_punct = len(punct_tokens)

    n_complex_punct = sum(token.text in COMPLEX_PUNCT for token in punct_tokens)

    # --------------------------------------------------------
    # Acentuação
    # --------------------------------------------------------

    tokens_with_accent = sum(
        any(char in ACCENTED_CHARS for char in token.text) for token in tokens
    )

    # --------------------------------------------------------
    # Verbos
    # --------------------------------------------------------

    verb_tokens = [token for token in tokens if token.pos_ == "VERB"]

    n_irregular = sum(token.lemma_.lower() in IRREGULAR_VERBS for token in verb_tokens)

    # Usa membership em vez de acessar [0] em uma lista
    # morfológica, que pode estar vazia.
    n_past = sum("Past" in token.morph.get("Tense") for token in verb_tokens)

    n_subjunctive = sum("Sub" in token.morph.get("Mood") for token in verb_tokens)

    # --------------------------------------------------------
    # Montagem das 31 features
    # --------------------------------------------------------

    features = [
        # Estruturais (0-4)
        n,
        len(sents),
        np.mean(sent_lengths) if sent_lengths else 0.0,
        np.mean([len(t.text) for t in tokens]),
        np.std([len(t.text) for t in tokens]),
        # Riqueza lexical (5-7)
        len(unique_lemmas) / n,
        len(set(t.lemma_ for t in tokens if t.pos_ == "NOUN"))
        / max(1, pos_counts.get("NOUN", 0)),
        len(set(t.lemma_ for t in tokens if t.pos_ == "VERB")) / max(1, n_verbs),
        # Proporções de classes gramaticais (8-15)
        pos_counts.get("NOUN", 0) / n,
        pos_counts.get("VERB", 0) / n,
        pos_counts.get("ADJ", 0) / n,
        pos_counts.get("ADP", 0) / n,
        pos_counts.get("CCONJ", 0) / n,
        pos_counts.get("SCONJ", 0) / n,
        pos_counts.get("PRON", 0) / n,
        pos_counts.get("ADV", 0) / n,
        # Sintaxe (16-19)
        np.mean(dependency_depths),
        np.max(dependency_depths),
        sum(token.dep_ in ("nmod", "amod", "acl", "advcl") for token in tokens) / n,
        float(has_passive),
        # Morfologia (20-24)
        sum(token.is_stop for token in tokens) / n,
        n_past / max(1, n_verbs),
        n_subjunctive / max(1, n_verbs),
        sum(len(token.text) > 8 for token in tokens) / n,
        sum(token.pos_ == "PROPN" for token in tokens) / n,
        # Canonicidade heurística (25-27)
        np.mean(canon_scores),
        pct_fully_canonical,
        np.std(canon_scores),
        # Características adicionais (28-30)
        n_complex_punct / max(1, n_punct),
        tokens_with_accent / n,
        n_irregular / max(1, n_verbs),
    ]

    if len(features) != len(SPACY_FEATURE_NAMES):
        raise ValueError(
            f"Foram geradas {len(features)} features, "
            f"mas eram esperadas {len(SPACY_FEATURE_NAMES)}."
        )

    return features


# ============================================================
# EXTRAÇÃO EM LOTES COM SPACY
# ============================================================


def extract_spacy_features(texts) -> np.ndarray:
    """
    Processa os documentos em lotes.

    A saída é uma matriz float32 de formato:
        número de documentos x 31 features
    """

    texts = list(texts)

    if not texts:
        return np.empty(
            (0, len(SPACY_FEATURE_NAMES)),
            dtype=np.float32,
        )

    docs = nlp.pipe(
        texts,
        batch_size=128,
        n_process=1,
    )

    features = np.asarray(
        [extract_features(doc) for doc in docs],
        dtype=np.float32,
    )

    expected_shape = (
        len(texts),
        len(SPACY_FEATURE_NAMES),
    )

    if features.shape != expected_shape:
        raise ValueError(
            f"Formato inesperado: {features.shape}. " f"Esperado: {expected_shape}."
        )

    return features


def prepare_input(texts) -> pd.DataFrame:
    """
    Prepara os dados para o pipeline completo.
    Usada também durante a inferência.
    """

    texts = [str(text) for text in texts]

    features = extract_spacy_features(texts)

    frame = pd.DataFrame(
        features,
        columns=SPACY_FEATURE_NAMES,
    )

    frame.insert(0, "text", texts)

    return frame


# ============================================================
# CARREGAMENTO DO DATASET
# ============================================================


def load_dataset():
    texts = []
    labels = []

    for subfolder, label in LABELS.items():
        folder = FOLDER / subfolder

        if not folder.is_dir():
            raise FileNotFoundError(
                "Pasta do dataset não encontrada: " f"{folder.resolve()}"
            )

        files = sorted(folder.glob("*.txt"))

        print(f"{label}: {len(files)} documentos")

        for txt_file in files:
            content = txt_file.read_text(
                encoding="utf-8",
                errors="replace",
            )

            texts.append(content)
            labels.append(label)

    if not texts:
        raise ValueError(
            "Nenhum arquivo .txt encontrado. "
            f"Verifique o diretório: {FOLDER.resolve()}"
        )

    return texts, np.asarray(labels)


# ============================================================
# PIPELINE DE CLASSIFICAÇÃO
# ============================================================


def build_pipeline(n_svd_components: int) -> Pipeline:

    text_pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=TFIDF_MAX_FEATURES,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    dtype=np.float32,
                ),
            ),
            (
                "svd",
                TruncatedSVD(
                    n_components=n_svd_components,
                    n_iter=7,
                    random_state=42,
                ),
            ),
        ]
    )

    features = ColumnTransformer(
        transformers=[
            (
                "text",
                text_pipeline,
                "text",
            ),
            (
                "spacy",
                "passthrough",
                SPACY_FEATURE_NAMES,
            ),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )

    classifier = HistGradientBoostingClassifier(
        max_iter=400,
        max_depth=6,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=42,
    )

    return Pipeline(
        [
            ("features", features),
            ("clf", classifier),
        ]
    )


# ============================================================
# TREINAMENTO E AVALIAÇÃO
# ============================================================


def main():

    total_start = time.perf_counter()

    # --------------------------------------------------------
    # 1. Carregar os documentos
    # --------------------------------------------------------

    print("=" * 65)
    print("CARREGAMENTO DO DATASET")
    print("=" * 65)

    texts, y = load_dataset()

    counts = {label: int(np.sum(y == label)) for label in CLASS_ORDER}

    print("\nDistribuição das classes:")

    for label, count in counts.items():
        print(f"  {label}: {count}")

    missing_classes = [label for label, count in counts.items() if count == 0]

    if missing_classes:
        raise ValueError(f"Classes sem documentos: {missing_classes}")

    if min(counts.values()) < 2:
        raise ValueError(
            "Cada classe precisa ter pelo menos "
            "2 documentos para o split estratificado. "
            "Idealmente, utilize mais amostras por classe."
        )

    # --------------------------------------------------------
    # 2. Extrair as features spaCy uma única vez
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("EXTRAÇÃO DAS FEATURES SPACY")
    print("=" * 65)

    start = time.perf_counter()

    spacy_features = extract_spacy_features(texts)

    X = pd.DataFrame(
        spacy_features,
        columns=SPACY_FEATURE_NAMES,
    )

    X.insert(0, "text", texts)

    elapsed = time.perf_counter() - start

    print(f"Documentos processados: {len(texts)}")
    print(f"Features por documento: {len(SPACY_FEATURE_NAMES)}")
    print(f"Tempo de extração spaCy: {elapsed:.2f}s")

    # --------------------------------------------------------
    # 3. Separar treino e teste
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("SEPARAÇÃO TREINO / TESTE")
    print("=" * 65)

    indices = np.arange(len(texts))

    idx_train, idx_test = train_test_split(
        indices,
        test_size=0.20,
        stratify=y,
        random_state=42,
    )

    X_train = X.iloc[idx_train].reset_index(drop=True)
    X_test = X.iloc[idx_test].reset_index(drop=True)

    y_train = y[idx_train]
    y_test = y[idx_test]

    print(f"Treino: {len(X_train)}")
    print(f"Teste:  {len(X_test)}")

    train_counts = {label: int(np.sum(y_train == label)) for label in CLASS_ORDER}

    if min(train_counts.values()) < 2:
        raise ValueError(
            "Há classes com menos de 2 documentos no treino. "
            "Aumente o dataset ou ajuste a estratégia de split."
        )

    # --------------------------------------------------------
    # 4. Configurar validação cruzada
    # --------------------------------------------------------

    n_splits = min(
        CV_FOLDS,
        min(train_counts.values()),
    )

    cv = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=42,
    )

    print(f"\nFolds da validação cruzada: {n_splits}")

    # Estimativa conservadora do menor treino dentro dos folds.
    smallest_cv_train = (len(X_train) * (n_splits - 1)) // n_splits

    n_svd_components = min(
        SVD_COMPONENTS,
        max(1, smallest_cv_train - 1),
    )

    print("Componentes SVD configurados: " f"{n_svd_components}")

    pipe = build_pipeline(n_svd_components)

    # --------------------------------------------------------
    # 5. Validação cruzada
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("VALIDAÇÃO CRUZADA")
    print("=" * 65)

    start = time.perf_counter()

    cv_results = cross_validate(
        pipe,
        X_train,
        y_train,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "f1_macro": "f1_macro",
        },
        n_jobs=1,
        return_train_score=False,
        error_score="raise",
    )

    cv_accuracy = cv_results["test_accuracy"]
    cv_f1_macro = cv_results["test_f1_macro"]

    print(f"Accuracy: {cv_accuracy.mean():.4f} " f"+/- {cv_accuracy.std():.4f}")

    print(f"F1 macro: {cv_f1_macro.mean():.4f} " f"+/- {cv_f1_macro.std():.4f}")

    print("Tempo da validação cruzada: " f"{time.perf_counter() - start:.2f}s")

    # --------------------------------------------------------
    # 6. Treinar o modelo final
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("TREINAMENTO FINAL")
    print("=" * 65)

    start = time.perf_counter()

    pipe.fit(X_train, y_train)

    print(f"Tempo de treinamento: " f"{time.perf_counter() - start:.2f}s")

    # --------------------------------------------------------
    # 7. Avaliar no conjunto de teste
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("AVALIAÇÃO NO CONJUNTO DE TESTE")
    print("=" * 65)

    y_pred = pipe.predict(X_test)

    acc = pipe.score(X_test, y_test)

    f1_macro = f1_score(
        y_test,
        y_pred,
        labels=CLASS_ORDER,
        average="macro",
        zero_division=0,
    )

    print(f"\nAccuracy: {acc:.4f}")
    print(f"F1 macro: {f1_macro:.4f}")

    print(
        "\nRelatório de classificação:\n",
        classification_report(
            y_test,
            y_pred,
            labels=CLASS_ORDER,
            target_names=CLASS_ORDER,
            zero_division=0,
        ),
    )

    print(
        "Matriz de confusão:\n",
        confusion_matrix(
            y_test,
            y_pred,
            labels=CLASS_ORDER,
        ),
    )

    # --------------------------------------------------------
    # 8. Importância das features
    # --------------------------------------------------------

    if CALCULAR_IMPORTANCIA:

        print("\n" + "=" * 65)
        print("IMPORTÂNCIA DAS FEATURES")
        print("=" * 65)

        start = time.perf_counter()

        X_test_transformed = pipe.named_steps["features"].transform(X_test)

        # as features textuais são componentes SVD,
        feature_names = [f"tfidf_svd_{i:03d}" for i in range(n_svd_components)] + [
            f"spacy__{name}" for name in SPACY_FEATURE_NAMES
        ]

        if X_test_transformed.shape[1] != len(feature_names):
            raise ValueError(
                "A quantidade de nomes das features não "
                "corresponde à matriz transformada."
            )

        clf = pipe.named_steps["clf"]

        perm = permutation_importance(
            clf,
            X_test_transformed,
            y_test,
            scoring="f1_macro",
            n_repeats=3,
            random_state=42,
            n_jobs=1,
        )

        top_features = sorted(
            zip(
                feature_names,
                perm.importances_mean,
            ),
            key=lambda item: item[1],
            reverse=True,
        )[:15]

        print("\nTop 15 features:")

        for name, importance in top_features:
            print(f"  {name:35s} {importance:.5f}")

        print(
            "\nTempo da análise de importância: " f"{time.perf_counter() - start:.2f}s"
        )

    # --------------------------------------------------------
    # 9. Salvar o modelo
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("SALVAMENTO")
    print("=" * 65)

    model_bundle = {
        "pipeline": pipe,
        "spacy_model": SPACY_MODEL,
        "labels": LABELS,
        "spacy_feature_names": SPACY_FEATURE_NAMES,
        "svd_components": n_svd_components,
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
        compress=3,
    )

    print(f"Modelo salvo em: {Path(MODEL_PATH).resolve()}")

    # --------------------------------------------------------
    # 10. Testar inferência
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("TESTE DE INFERÊNCIA")
    print("=" * 65)

    exemplo = (
        "A fotossíntese é um processo bioquímico pelo qual "
        "organismos autotróficos convertem energia luminosa "
        "em energia química."
    )

    resultado = predizer(exemplo, pipeline=pipe)

    print(f"Texto: {exemplo}")
    print(f"Resultado: {resultado}")

    print(f"\nTempo total: " f"{time.perf_counter() - total_start:.2f}s")


# ============================================================
# INFERÊNCIA
# ============================================================


def predizer(texto: str, pipeline=None) -> dict:
    """
    Recebe um texto e retorna a classe predita e as probabilidades.

    Pode usar o pipeline treinado na sessão atual ou um pipeline
    carregado de um arquivo joblib.
    """

    if pipeline is None:
        bundle = joblib.load(MODEL_PATH)
        pipeline = bundle["pipeline"]

    entrada = prepare_input([texto])

    probabilidades = pipeline.predict_proba(entrada)[0]
    label = pipeline.predict(entrada)[0]
    classes = list(pipeline.classes_)

    return {
        "nivel": label,
        "confianca": float(probabilidades[classes.index(label)]),
        "todas": {
            classe: float(probabilidade)
            for classe, probabilidade in zip(
                classes,
                probabilidades,
            )
        },
    }


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
