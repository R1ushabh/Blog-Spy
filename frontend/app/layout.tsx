import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "Competitor Blog Spy & Real-Time Content Monitoring System",
  description: "Academic Production Monitoring Architecture with Exact Delay Math and Multi-Strategy Detection",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 flex min-h-screen antialiased">
        <Sidebar sseConnected={true} />
        <main className="flex-1 overflow-y-auto min-h-screen bg-zinc-950 p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
