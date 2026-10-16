import Link from "next/link";

const year = new Date().getFullYear() ;

export default function Footer() {

    return (
        <footer className="text-content font-primary self-center text-xs py-6 border-t border-content/10">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                <p>
                    © {year} Gerador Textual Multinível. Todos os direitos reservados.
                </p>

                <div className="flex gap-4">
                    <Link
                        href="https://www.linkedin.com/in/arthuralonsomarcelino/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-primary"
                    >
                        LinkedIn
                    </Link>
                    <Link
                        href="https://github.com/Alieinstein2008"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-primary"
                    >
                        GitHub
                    </Link>
                </div>
            </div>
        </footer>
    );
}   