import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Focus Platform Training",
  description: "منصة تكوينية داخلية — مركز Focus، سافي، المغرب",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body className="min-h-screen font-cairo">{children}</body>
    </html>
  );
}
