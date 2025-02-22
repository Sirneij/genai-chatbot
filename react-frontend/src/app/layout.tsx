import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ThemeSwitcher from "$/app/ui/layout/ThemeSwitcher";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Chatbot with Next.js and Python | John Owolabi Idogun",
  description:
    "Build an AI chatbot with Next.js and Python using WebSockets by John Owolabi Idogun.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased font-[family-name:var(--font-geist-sans)] bg-[#ffffff] text-[#171717] dark:bg-[#0a0a0a] dark:text-[#ededed] min-h-screen`}
      >
        <ThemeSwitcher />
        <main className="flex flex-col min-h-screen mx-auto max-w-10/12">
          <div className="flex-1 w-full">{children}</div>
        </main>
      </body>
    </html>
  );
}
