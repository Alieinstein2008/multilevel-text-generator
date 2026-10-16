export interface Prediction {
    level: "EF1" | "EF2" | "EM" | "ES";
    confidence: number;
    all: Record<string, number>;
}

export interface Operations {
    wordSwap: boolean;
    genderSwap: boolean;
    paraphrase: boolean;
}

export interface GenerationResult {
    originalText: string;
    resultText: string;
    originalPrediction: Prediction;
    resultPrediction: Prediction;
    appliedOperations: Operations;
}

export interface Prediction {
  level: "EF1" | "EF2" | "EM" | "ES";
  confidence: number;
  all: Record<string, number>;
}

export interface Operations {
  wordSwap: boolean;
  genderSwap: boolean;
  paraphrase: boolean;
}

export interface GenerationResponse {
  originalText: string;
  resultText: string;
  appliedOperations: Operations;
}

export interface GenerationResult extends GenerationResponse {
  originalPrediction: Prediction;
  resultPrediction: Prediction;
}

export interface TextStatistics {
  wordCount: number;
  sentenceCount: number;
  canonicalWordCount: number;
  canonicalWordPercentage: number;
  averageWordLength: number;
  lexicalDiversity: number;
}

export interface GenerationResult {
  originalText: string;
  resultText: string;
  originalPrediction: Prediction;
  resultPrediction: Prediction;
  appliedOperations: Operations;

  originalStats: TextStatistics;
  resultStats: TextStatistics;
}