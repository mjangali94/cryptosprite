import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "../components/Sidebar"
import Header from "../components/Header"

export const metadata: Metadata = {
  title: "Crypto trading agent",
  description: "AI-powered crypto trading assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen flex bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="p-6">{children}</main>
      </div>
      </body>
    </html>
  );
}
