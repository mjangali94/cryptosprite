"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "AI Agent", path: "/agents" },
  ];

  return (
    <aside className="w-64 bg-white shadow-lg p-6 flex flex-col h-screen sticky top-0">
      <h1 className="text-2xl font-bold mb-8 text-teal-500 font-sans">CryptoSprite</h1>

      <nav className="flex flex-col gap-4">
        {links.map((link) => {
          const isActive = pathname.startsWith(link.path);
          return (
            <Link
              key={link.path}
              href={link.path}
              className={`p-3 rounded-xl font-medium ${
                isActive ? "bg-blue-600 text-white shadow-md" : "text-gray-700 hover:bg-gray-200"
              }`}
            >
              {link.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}