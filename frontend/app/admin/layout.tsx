"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { logout } from "@/lib/api";

const NAV = [
  { href: "/admin/dashboard", label: "لوحة القيادة / Tableau de bord", icon: "📊" },
  { href: "/admin/content", label: "المحتويات / Contenus", icon: "📚" },
  { href: "/admin/content/drafts", label: "المسودات / Brouillons", icon: "📝" },
  { href: "/admin/pipeline", label: "AI Pipeline", icon: "🤖" },
  { href: "/admin/users", label: "المستخدمون / Utilisateurs", icon: "👥" },
  { href: "/admin/analytics", label: "التحليلات / Analytique", icon: "📈" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 bg-dark p-4 text-white">
        <p className="mb-6 px-2 font-bold">
          Focus Admin
          <span className="mt-1 block text-xs font-normal text-slate-400">لوحة الأدمين / Admin</span>
        </p>
        <nav className="space-y-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-3 py-2 text-sm transition ${
                pathname === item.href ? "bg-primary text-white" : "text-slate-300 hover:bg-white/10"
              }`}
            >
              {item.icon} {item.label}
            </Link>
          ))}
        </nav>
        <button
          onClick={async () => {
            await logout();
            router.replace("/login");
          }}
          className="mt-8 w-full rounded-lg bg-white/10 px-3 py-2 text-sm hover:bg-white/20"
        >
          خروج / Déconnexion
        </button>
      </aside>
      <main className="min-w-0 flex-1 p-6">{children}</main>
    </div>
  );
}
