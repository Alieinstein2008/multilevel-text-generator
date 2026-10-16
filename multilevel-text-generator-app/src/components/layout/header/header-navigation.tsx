"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
    { href: "/home", label: "Oficina de Texto" },
    { href: "/about", label: "Como Funciona" },
    { href: "/contact", label: "Ajuda" },
];

export default function HeaderNavigation() {
    const pathname = usePathname();

    return (
        <nav className="text-content h-full font-medium text-xs flex items-center">
            <ul className="flex gap-x-3 items-baseline">
                {links.map(({ href, label }) => (
                    <li key={href}>
                        <Link
                            href={href}
                            className={
                                pathname === href
                                    ? " text-primary"
                                    : "hover:text-gray-500"
                            }
                        >
                            {label}
                        </Link>
                    </li>
                ))}
            </ul>
        </nav>
    );
}   