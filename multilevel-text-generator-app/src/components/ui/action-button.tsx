"use client";

import { LucideIcon } from "lucide-react";

interface Props {
  message: string;
  backgroundColor: "primary" | "surface" | "surface-alt";
  textColor: "white" | "black" | "content" | "content-muted";
  iconSize: number;
  icon: LucideIcon;
  onClickAction: () => void;
  disabled?: boolean;
}

const bgMap: Record<string, string> = {
  primary: "bg-primary",
  surface: "bg-surface",
  surfaceAlt: "bg-surface-alt"
};

const textMap: Record<string, string> = {
  white: "text-white",
  black: "text-black",
  content: "text-content",
  "content-muted": "text-content-muted",
};

export default function ActionButton({ message, backgroundColor, textColor, iconSize, icon: Icon, onClickAction, disabled = false }: Props) {
  return (
    <button
      onClick={onClickAction}
      disabled={disabled}
      className={`${bgMap[backgroundColor]} ${textMap[textColor]} cursor-pointer flex items-center rounded-xl font-medium text-xs gap-x-2 justify-center w-auto h-8.5 p-2 border border-content-muted/30 disabled:opacity-50 disabled:cursor-not-allowed`}>
      <Icon size={iconSize}></Icon>
      {message}
    </button>
  );
}   