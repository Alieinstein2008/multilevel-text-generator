import type {
  GenerationResponse,
  Operations,
  Prediction,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

function getApiUrl(): string {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL não foi configurada.");
  }

  return API_URL;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(
      data?.detail ??
        data?.message ??
        `Erro na API: ${response.status}`
    );
  }

  return data as T;
}

export async function generateText(
  text: string,
  operations: Operations
): Promise<GenerationResponse> {
  const response = await fetch(`${getApiUrl()}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, operations }),
  });

  return parseResponse<GenerationResponse>(response);
}

interface ClassificationApiResponse {
  nivel: Prediction["level"];
  confianca: number;
  todas: Record<string, number>;
}

export async function classifyText(
  text: string
): Promise<Prediction> {
  const response = await fetch(`${getApiUrl()}/classify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  const data =
    await parseResponse<ClassificationApiResponse>(response);

  return {
    level: data.nivel,
    confidence: data.confianca,
    all: data.todas,
  };
}