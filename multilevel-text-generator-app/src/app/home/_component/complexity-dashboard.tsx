"use client"

import ComplexityLevel from "@/components/ui/complexity-level"
import { Prediction } from "@/types";
import { ChartNoAxesColumnIncreasing, ArrowRight } from "lucide-react"

interface Props {
    originalPrediction: Prediction | null;
    resultPrediction: Prediction | null;
}

const LEVELS = [
    "Ensino Fundamental I",
    "Ensino Fundamental II",
    "Ensino Médio",
    "Ensino Superior"
];

const LEVEL_KEYS: Record<string, string> = {
    "EF1": "Ensino Fundamental I",
    "EF2": "Ensino Fundamental II",
    "EM": "Ensino Médio",
    "ES": "Ensino Superior"
}

export default function ComplexityDashboard({ originalPrediction, resultPrediction }: Props) {
    return (
        <div className="w-83/100 self-center border border-content-muted/35 rounded-xl p-4 flex flex-col gap-y-4 select-none">
            <div className="flex text-xs items-center gap-x-2">
                <ChartNoAxesColumnIncreasing size={18} className="text-primary" />
                <h3 className="uppercase font-semibold text-content-muted">Complexidade do Texto</h3>
            </div>
            <div className="flex items-center w-full justify-center">
                <div className="flex flex-col gap-y-2 w-full">
                    <p className="text-black text-xs font-semibold">Inicial · texto de entrada</p>
                    <div className="flex gap-x-2 w-full h-full">
                        {LEVELS.map((name, i) => (
                            <ComplexityLevel
                                key={i}
                                levelName={name}
                                active={originalPrediction ? LEVEL_KEYS[originalPrediction.level] === name : false}
                            />
                        ))}
                    </div>
                </div>
                <div>
                    <div className="w-8 h-8 rounded-full flex items-center justify-center bg-secondary mx-6">
                        <ArrowRight className="text-surface"></ArrowRight>
                    </div>
                </div>
                <div className="flex flex-col gap-y-2 w-full ">
                    <p className="text-black text-xs font-semibold">Inicial · texto de entrada</p>
                    <div className="flex gap-2 w-full h-full">
                        {LEVELS.map((name, i) => (
                            <ComplexityLevel
                                key={i}
                                levelName={name}
                                active={resultPrediction ? LEVEL_KEYS[resultPrediction.level] === name : false}
                            />
                        ))}  </div>

                </div>
            </div>
        </div>
    )
}

