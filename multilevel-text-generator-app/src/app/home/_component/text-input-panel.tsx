"use client"

import ActionButton from "@/components/ui/action-button";
import MutationOperationButton from "@/app/home/_component/mutation-operation-button"
import { NotebookPen, ReplaceAll, UsersRound, TextWrap, Sparkles } from "lucide-react"
import { Operations } from "@/types";

const mutationOperations = [
    {
        key: "wordSwap" as const,
        title: "Troca de Palavras",
        subtitle: "Substitui palavras do texto original por sinônimos ou antônimos.",
        icon: ReplaceAll,
        disabled: false
    },
    {
        key: "genderSwap" as const,
        title: "Troca de Gênero",
        subtitle: "Altera automaticamente o gênero de algumas frases no texto.",
        icon: UsersRound,
        disabled: false
    },
    {
        key: "paraphrase" as const,
        title: "Paráfrase",
        subtitle: "Indisponível no momento.",
        icon: TextWrap,
        disabled: true
    }
];

interface Props {
    text: string;
    setText: (v: string) => void;
    operations: Operations;
    setOperations: (v: Operations) => void;
    onGenerate: () => void;
    loading: boolean;
}

export default function TextInputPanel({ text, setText, operations, setOperations, onGenerate, loading }: Props) {

    const toggleOp = (key: keyof Operations) => {
        if(key == "paraphrase") return;
        setOperations({ ...operations, [key]: !operations[key] });
    }

    return (
        <article className="w-40/100 h-fit rounded-2xl border border-content-muted/35">
            <header className="flex gap-x-1.5 items-center border-b w-full h-12 border-content-muted/35 font-semibold capitalize text-sm px-4">
                <NotebookPen className="text-primary" size={18} />
                <h2 className="text-content">Seu texto</h2>
            </header>
            <div className="p-4 flex flex-col gap-y-3 text-">
                <textarea
                    className="w-full rounded-2xl border scrollbar-thin border-content-muted/35 pr-4 pl-4 pt-2 pb-2 resize-none text-content-muted placeholder:text-content-muted/50 focus:outline-none focus:ring-1 focus:ring-content-muted/20 text-xs focus:border-content-muted/20"
                    rows={10}
                    placeholder="Escreva seu texto aqui..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                ></textarea>
                <div className="w-full flex flex-col gap-y-4 text-content">
                    <div className="w-full h-fit font-primary">
                        <h3 className="text-md font-semibold">Operações de Mutação</h3>
                        <p className="text-content-muted text-xs">Combine as operações que deseja aplicar ao texto.</p>
                    </div>
                    <div className="flex flex-col gap-y-2 text-xs">
                        {mutationOperations.map((op) => (
                            <MutationOperationButton
                                key={op.key}
                                title={op.title}
                                subtitle={op.subtitle}
                                icon={op.icon}
                                active={operations[op.key]}
                                onToggle={() => toggleOp(op.key)}
                                disabled={op.disabled}
                            />
                        ))}

                        <div className="w-full flex items-center justify-between">
                            <button
                                onClick={() => setText("")}
                                className="text-xs cursor-pointer text-content-muted/60">
                                Limpar texto

                            </button>
                            <ActionButton
                                onClickAction={onGenerate}
                                icon={Sparkles}
                                message={loading ? "Generating..." : "Generate"}
                                textColor="white"
                                backgroundColor="primary"
                                iconSize={20}
                                disabled={loading || !text.trim()}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </article>
    );
}