import { TextCursorInput } from "lucide-react";
import HeaderNavigation from "./header-navigation";

export default function Header() {
    return (
        <header className="w-full h-14 border-b flex pl-8 pr-8 border-content/10 justify-between">
            <div className="flex justify-center items-center gap-x-4">
                <span className="rounded-2xl w-10 h-10 bg-primary flex items-center justify-center">
                    <TextCursorInput size={20} />
                </span>
                <h1 className="text-content text-md font-semibold capitalize">Gerador Textual Multinível</h1>
            </div>
            <HeaderNavigation></HeaderNavigation>
        </header>
    )
}