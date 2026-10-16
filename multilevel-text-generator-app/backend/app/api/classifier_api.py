import logging
from pathlib import Path

import joblib
import numpy as np

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ml.complexity_classifier import (
    prepare_input,
    SPACY_MODEL,
    nlp,
    canonicity_score,
)

from app.services.text_operations import apply_text_operations

logger = logging.getLogger(__name__)

from pathlib import Path

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "ml"
    / "models"
    / "modelo_complexidade.joblib"
)

# ============================================================
# CARREGAMENTO DO MODELO
# ============================================================

if not MODEL_PATH.is_file():
    raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")

bundle = joblib.load(MODEL_PATH)

PIPELINE = bundle["pipeline"]

SAVED_SPACY_MODEL = bundle.get("spacy_model")

if SAVED_SPACY_MODEL and SAVED_SPACY_MODEL != SPACY_MODEL:
    raise RuntimeError(
        "O modelo spaCy configurado não corresponde "
        "ao modelo utilizado no treinamento: "
        f"{SAVED_SPACY_MODEL!r} != {SPACY_MODEL!r}"
    )


# ============================================================
# API
# ============================================================

router = APIRouter(
    prefix="/api",
    tags=["Texto e classificação"],
)


class ClassificationRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=100_000,
    )


class OperationsRequest(BaseModel):
    wordSwap: bool = False
    genderSwap: bool = False
    paraphrase: bool = False


class GenerateRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=100_000,
    )

    operations: OperationsRequest = Field(
        default_factory=OperationsRequest,
    )


# ============================================================
# CLASSIFICAÇÃO
# ============================================================


def predict_texts(texts: list[str]) -> list[dict]:
    """
    Classifica um ou mais textos usando o pipeline treinado.

    Processa as features dos textos em uma única chamada,
    evitando repetir chamadas desnecessárias ao spaCy.
    """

    if not texts:
        return []

    features = prepare_input(texts)

    probabilities_batch = PIPELINE.predict_proba(features)
    classes = [str(label) for label in PIPELINE.classes_]

    predictions = []

    for probabilities in probabilities_batch:
        best_index = int(np.argmax(probabilities))

        predictions.append(
            {
                "level": classes[best_index],
                "confidence": float(probabilities[best_index]),
                "all": {
                    label: float(probability)
                    for label, probability in zip(
                        classes,
                        probabilities,
                    )
                },
            }
        )

    return predictions


def predict_text(text: str) -> dict:
    """Classifica um único texto."""

    return predict_texts([text])[0]


# ============================================================
# RELATÓRIO
# ============================================================


def analyze_text_stats(text: str) -> dict:
    """
    Calcula indicadores descritivos do texto.

    A proporção de palavras canônicas utiliza a mesma função
    heurística de canonicidade do classificador, considerando
    somente tokens alfabéticos no denominador.
    """

    doc = nlp(text)

    words = [token for token in doc if token.is_alpha]

    sentences = [
        sentence for sentence in doc.sents if any(token.is_alpha for token in sentence)
    ]

    word_count = len(words)

    canonical_word_count = sum(canonicity_score(token.text) == 1.0 for token in words)

    lemmas = [token.lemma_.casefold() for token in words if token.lemma_]

    canonical_percentage = (
        canonical_word_count / word_count * 100 if word_count else 0.0
    )

    average_word_length = (
        sum(len(token.text) for token in words) / word_count if word_count else 0.0
    )

    lexical_diversity = len(set(lemmas)) / len(lemmas) * 100 if lemmas else 0.0

    return {
        "wordCount": word_count,
        "sentenceCount": len(sentences),
        "canonicalWordCount": canonical_word_count,
        "canonicalWordPercentage": round(canonical_percentage, 2),
        "averageWordLength": round(average_word_length, 2),
        "lexicalDiversity": round(lexical_diversity, 2),
    }


# ============================================================
# GERAÇÃO + CLASSIFICAÇÃO
# ============================================================


@router.post("/generate")
def generate_text(payload: GenerateRequest):
    original_text = payload.text.strip()

    if not original_text:
        raise HTTPException(
            status_code=422,
            detail="Informe um texto para transformar.",
        )

    operations = payload.operations.dict()

    if operations["paraphrase"]:
        raise HTTPException(
            status_code=422,
            detail=("A operação de paráfrase " "está indisponível no momento."),
        )

    try:
        result_text, applied_operations = apply_text_operations(
            original_text,
            operations,
        )

        original_prediction, result_prediction = predict_texts(
            [
                original_text,
                result_text,
            ]
        )

        original_stats = analyze_text_stats(original_text)
        result_stats = analyze_text_stats(result_text)

        return {
            "originalText": original_text,
            "resultText": result_text,
            "originalPrediction": original_prediction,
            "resultPrediction": result_prediction,
            "appliedOperations": applied_operations,
            "originalStats": original_stats,
            "resultStats": result_stats,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Erro durante a geração e classificação.")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível processar o texto.",
        )


# ============================================================
# CLASSIFICAÇÃO ISOLADA
# ============================================================


@router.post("/classify")
def classify_text(payload: ClassificationRequest):
    text = payload.text.strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail="Informe um texto para classificação.",
        )

    try:
        prediction = predict_text(text)

        return {
            "nivel": prediction["level"],
            "confianca": prediction["confidence"],
            "todas": prediction["all"],
        }

    except Exception:
        logger.exception("Erro durante a classificação do texto.")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível classificar o texto.",
        )
