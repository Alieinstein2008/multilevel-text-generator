"use client"

import ActionButton from "@/components/ui/action-button";
import { FileCheckCorner, Copy, BarChart3, Info, X } from "lucide-react";
import type { GenerationResult } from "@/types";
import { useState } from "react";

interface Props {
    result: GenerationResult | null;
}

const SHORT_TEXT_THRESHOLD = 100;

function formatNumber(value: number, digits = 1) {
    return value.toLocaleString("pt-BR", {
        maximumFractionDigits: digits,
    });
}

export default function OutputTextPanel({ result }: Props) {
    const stats = result?.resultStats;

    const activeCount = result
        ? Number(result.appliedOperations.wordSwap) +
        Number(result.appliedOperations.genderSwap)
        : 0;

    const [showShortTextInfo, setShowShortTextInfo] = useState(false);

    const isShortText = Boolean(
        result &&
        (
            (result.originalStats?.wordCount ?? Infinity) < SHORT_TEXT_THRESHOLD ||
            (result.resultStats?.wordCount ?? Infinity) < SHORT_TEXT_THRESHOLD
        )
    );

    const canonicalPercentage = Math.min(
        100,
        Math.max(0, stats?.canonicalWordPercentage ?? 0)
    );

    async function handleCopy() {
        if (!result) return;

        try {
            await navigator.clipboard.writeText(result.resultText);
        } catch (error) {
            console.error("Erro ao copiar texto:", error);
        }
    }

    return (
        <article className="w-40/100 h-fit rounded-2xl border border-content-muted/35">

            <header className="flex h-12 w-full items-center justify-between border-b border-content-muted/35 px-4">
                <div className="flex items-center gap-x-1.5 text-sm font-semibold">
                    <FileCheckCorner className="text-primary" size={18} />

                    <h2 className="text-content">
                        Texto Resultante
                    </h2>
                </div>

                {isShortText && (
                    <div className="relative">
                        <button
                            type="button"
                            onClick={() =>
                                setShowShortTextInfo((previous) => !previous)
                            }
                            aria-label="Informações sobre textos curtos"
                            aria-expanded={showShortTextInfo}
                            aria-controls="short-text-info-popup"
                            className="flex h-7 w-7 items-center justify-center rounded-full
                    text-content-muted transition-colors
                    hover:bg-content-muted/10 hover:text-primary
                    focus-visible:outline-none focus-visible:ring-2
                    focus-visible:ring-primary/40"
                        >
                            <Info size={17} />
                        </button>

                        {showShortTextInfo && (
                            <div
                                id="short-text-info-popup"
                                role="dialog"
                                aria-label="Aviso sobre textos curtos"
                                className="absolute right-0 top-full z-50 mt-2 w-64
                        rounded-xl border border-content-muted/20
                        bg-white p-4 shadow-lg"
                            >
                                <div className="mb-2 flex items-start justify-between gap-3">
                                    <h3 className="text-xs font-semibold text-content">
                                        Atenção a textos curtos
                                    </h3>

                                    <button
                                        type="button"
                                        onClick={() => setShowShortTextInfo(false)}
                                        aria-label="Fechar aviso"
                                        className="shrink-0 rounded-md p-0.5
                                text-content-muted hover:text-content"
                                    >
                                        <X size={15} />
                                    </button>
                                </div>

                                <p className="text-xs leading-relaxed text-content-muted">
                                    Textos com menos de {SHORT_TEXT_THRESHOLD} palavras
                                    podem oferecer menos evidências linguísticas para
                                    a classificação. O modelo foi treinado com documentos
                                    completos, portanto a previsão para trechos curtos
                                    pode ser menos representativa.
                                </p>
                            </div>
                        )}
                    </div>
                )}
            </header>

            <div className="flex flex-col gap-y-3 p-4">

                <textarea
                    className="w-full resize-none rounded-xl border border-content-muted/35 p-3 text-xs text-content-muted focus:outline-none"
                    rows={10}
                    disabled
                    value={result?.resultText ?? ""}
                    placeholder="O texto gerado aparecerá aqui..."
                />

                <div className="w-full flex flex-col gap-y-4 text-content">
                    <div>
                        <h3 className="text-sm font-semibold text-content">
                            Operações aplicadas
                        </h3>
                        <p className="text-xs text-content-muted">
                            {activeCount} de 2 operações
                        </p>
                    </div>

                    <ActionButton
                        onClickAction={handleCopy}
                        icon={Copy}
                        message="Copiar"
                        textColor="black"
                        backgroundColor="surface-alt"
                        iconSize={16}
                        disabled={!result}
                    />
                </div>

                {stats && (
                    <section className="border-t border-content-muted/20 pt-3">
                        <div className="mb-2 flex items-center gap-2">
                            <BarChart3 size={20} className="text-primary" />
                            <h3 className="text-sm font-semibold text-content">
                                Indicadores linguísticos
                            </h3>
                        </div>

                        <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                            <div>
                                <p className="text-xs text-content-muted">
                                    Palavras
                                </p>
                                <p className="text-sm font-semibold text-content">
                                    {stats.wordCount}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-content-muted">
                                    Sentenças
                                </p>
                                <p className="text-sm font-semibold text-content">
                                    {stats.sentenceCount}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-content-muted">
                                    Média de caracteres
                                </p>
                                <p className="text-sm font-semibold text-content">
                                    {formatNumber(stats.averageWordLength)}
                                </p>
                            </div>

                            <div>
                                <p className="text-xs text-content-muted">
                                    Diversidade lexical
                                </p>
                                <p className="text-sm font-semibold text-content">
                                    {formatNumber(stats.lexicalDiversity)}%
                                </p>
                            </div>
                        </div>

                        <div className="mt-3 border-t border-content-muted/15 pt-3">
                            <div className="mb-1 flex items-center justify-between gap-2">
                                <p className="text-xs text-content-muted">
                                    Palavras canônicas*
                                </p>
                                <p className="text-xs font-semibold text-content">
                                    {formatNumber(canonicalPercentage)}%
                                    <span className="ml-1 font-normal text-content-muted">
                                        ({stats.canonicalWordCount}/{stats.wordCount})
                                    </span>
                                </p>
                            </div>

                            <div
                                className="h-1.5 overflow-hidden rounded-full bg-content-muted/15"
                                role="progressbar"
                                aria-label="Percentual de palavras canônicas"
                                aria-valuemin={0}
                                aria-valuemax={100}
                                aria-valuenow={canonicalPercentage}
                            >
                                <div
                                    className="h-full rounded-full bg-primary transition-all"
                                    style={{ width: `${canonicalPercentage}%` }}
                                />
                            </div>

                            <p className="mt-1 text-[10px] text-content-muted">
                                *Medida heurística de canonicidade.
                            </p>
                        </div>
                    </section>
                )}
            </div>
        </article>
    );
}
