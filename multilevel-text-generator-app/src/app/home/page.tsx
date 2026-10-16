"use client";

import { useState } from "react";

import {
  classifyText,
  generateText,
} from "@/services/api";

import type {
  GenerationResult,
  Operations,
} from "@/types";

import Footer from "@/components/layout/footer/footer";
import Header from "@/components/layout/header/header";
import TextInputPanel from "./_component/text-input-panel";
import ComplexityDashboard from "./_component/complexity-dashboard";
import OutputTextPanel from "./_component/text-output-panel";

export default function Home() {
  const [text, setText] = useState("");

  const [operations, setOperations] = useState<Operations>({
    wordSwap: false,
    genderSwap: false,
    paraphrase: false
  });

  const [result, setResult] = useState<GenerationResult | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  async function handleGenerate() {
    if (!text.trim()) {
      setError("Digite um texto antes de continuar.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const generated = await generateText(text, operations);

      const originalPrediction = await classifyText(
        generated.originalText
      );

      const resultPrediction = await classifyText(
        generated.resultText
      );

      setResult({
        ...(generated as GenerationResult),
        originalPrediction,
        resultPrediction,
      });
    } catch (e) {
      console.error("Erro ao gerar ou classificar texto:", e);

      setError(
        e instanceof Error
          ? e.message
          : "Não foi possível processar o texto."
      );

      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-1 flex-col items-center justify-center bg-zinc-50 font-primary">
      <Header />

      <main className="flex w-full flex-1 flex-col gap-x-2 gap-y-8 bg-white px-8 py-10 sm:items-start">
        <article className="h-fit w-full">
          <h1 className="text-2xl font-semibold text-content">
            Uma história, novas possibilidades.
          </h1>

          <p className="text-content-muted">
            Explore formas de reescrever uma narrativa e compare
            seus níveis de complexidade.
          </p>
        </article>

        <ComplexityDashboard
          originalPrediction={result?.originalPrediction ?? null}
          resultPrediction={result?.resultPrediction ?? null}
        />

        {error && (
          <div
            role="alert"
            className="w-full rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        <article className="flex h-fit w-full flex-1 justify-center gap-x-10">
          <TextInputPanel
            text={text}
            setText={setText}
            operations={operations}
            setOperations={setOperations}
            onGenerate={handleGenerate}
            loading={loading}
          />
          <OutputTextPanel result={result} />
        </article>
      </main>
      <Footer />
    </div>
  );
}