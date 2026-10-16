import { Construction, ArrowLeftIcon } from "lucide-react";

import Link from "next/link";

export default function Contact() {
    return (
        <div className="h-dvh w-dvw bg-white flex flex-col items-center justify-center gap-6 p-8 text-center">

            <h1 className="text-4xl font-extrabold text-gray-300">Em breve...</h1>

            <div className="w-full max-w-xl flex flex-col justify-between items-center text-black/80">
                <Construction size={200}></Construction>
                <Link
                    href={"/home"}
                    className="text-primary/70 text-2xl font-primary font-semibold flex justify-center gap-x-2 items-center"
                >
                    <ArrowLeftIcon></ArrowLeftIcon>
                    Voltar</Link>

            </div>

        </div>
    );

}