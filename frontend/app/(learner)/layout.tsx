"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/api";

export default function LearnerLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  return (
    <div className="min-h-screen">
      <nav className="bg-dark text-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
          <Link href="/dashboard" className="font-bold">
            Focus Platform Training
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <Link href="/dashboard" className="hover:text-blue-300">
              الرئيسية / Accueil
            </Link>
            <Link href="/certificates" className="hover:text-blue-300">
              شهاداتي / Mes certificats
            </Link>
            <button
              onClick={async () => {
                await logout();
                router.replace("/login");
              }}
              className="rounded-lg bg-white/10 px-3 py-1.5 hover:bg-white/20"
            >
              خروج / Déconnexion
            </button>
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}
