import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1] / "app" / "data" / "lexicon"

INPUT_PATH = BASE_DIR / "input.txt"
OUTPUT_PATH = BASE_DIR / "output.json"

RELATION_MAP = {
    "SYNONYMOUS_OF": "synonyms",
    "ANTONYM_OF": "antonyms",
}

data = {}


def add_relation(category: str, word: str, relation: str, other: str):
    category_data = data.setdefault(category, {})

    word_data = category_data.setdefault(
        word,
        {
            "synonyms": [],
            "antonyms": [],
        },
    )

    if other not in word_data[relation]:
        word_data[relation].append(other)


if not INPUT_PATH.is_file():
    raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT_PATH}")


with INPUT_PATH.open(encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        if not line:
            continue

        match = re.match(
            r"^\[(?P<category>[^\]]+)\]\s*"
            r"(?P<word1>.+?)\s+"
            r"(?P<relation>SYNONYMOUS_OF|ANTONYM_OF)\s+"
            r"(?P<word2>.+?)\s*$",
            line,
        )

        if not match:
            print(f"Linha {line_number} ignorada: " f"formato não reconhecido.")
            continue

        category = match.group("category").strip().lower()
        word1 = match.group("word1").strip().casefold()
        word2 = match.group("word2").strip().casefold()
        relation = RELATION_MAP[match.group("relation")]

        add_relation(category, word1, relation, word2)

        add_relation(category, word2, relation, word1)


with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2,
    )

total_words = sum(len(words) for words in data.values())

print(f"Categorias: {len(data)}")
print(f"Entradas lexicais: {total_words}")
print(f"Dicionário salvo em: {OUTPUT_PATH}")
