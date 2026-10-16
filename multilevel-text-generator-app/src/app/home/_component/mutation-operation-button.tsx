"use client"

import { LucideIcon, Check } from "lucide-react";
import { Key } from "react";

interface Props {
    key: Key;
    title: string;
    subtitle: string;
    icon: LucideIcon;
    active?: boolean;
    onToggle?: () => void;
    disabled?: boolean;
}

export default function MutationOperationButton({
    title,
    subtitle,
    icon: Icon,
    active = false,
    onToggle,
    disabled = false,

}: Props) {
    return (
        <label
            aria-disabled={disabled}
            className={`w-full min-h-14 flex items-center p-4 gap-2 rounded-xl
                text-[.65rem] wrap-break-word overflow-clip
                border border-surface bg-secondary
                ${disabled
                    ? "cursor-not-allowed opacity-50"
                    : "cursor-pointer"
                }`}
        >
            <input
                type="checkbox"
                className="peer sr-only"
                checked={active}
                disabled={disabled}
                onChange={disabled ? undefined : onToggle}
            />

            <div className="w-5 h-5 shrink-0 border-2 border-gray-300 rounded peer-checked:bg-surface peer-checked:border-surface flex items-center justify-center transition peer-checked:[&>svg]:opacity-100">
                <Check
                    size={14}
                    className="opacity-0 transition text-white"
                />
            </div>

            <div className="flex flex-col w-full select-none">
                <h4 className="font-semibold text-content">
                    {title}
                </h4>

                <p className={disabled
                    ? "text-content"
                    : "text-content-muted"
                }>
                    {subtitle}
                </p>
            </div>

            <Icon
                size={26}
                className="shrink-0 text-surface"
            />
        </label>
    );
}
