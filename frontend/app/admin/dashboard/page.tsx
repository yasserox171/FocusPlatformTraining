"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface AdminDashboard {
  learners_count: number;
  content_count: number;
  certificates_count: number;
  pending_drafts: {
    id: string;
    type: string;
    title_ar: string;
    title_fr: string;
    is_ai_generated: boolean;
  }[];
  recent_activity: {
    id: string;
    type: string;
    title_ar: string;
    title_fr: string;
    status: string;
  }[];
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl bg-white p-6 shadow-sm">
      <p className="text-3xl font-bold text-primary">{value}</p>
      <p className="mt-1 text-sm text-slate-500">{label}</p>
    </div>
  );
}

export default function AdminDashboardPage() {
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<AdminDashboard>("/api/admin/dashboard").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>;
  if (!data) return <p className="text-slate-500">جارٍ التحميل / Chargement...</p>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">لوحة القيادة / Tableau de bord</h1>
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="المتعلمون / Apprenants" value={data.learners_count} />
        <Stat label="المحتويات / Contenus" value={data.content_count} />
        <Stat label="الشهادات / Certificats" value={data.certificates_count} />
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-bold">مسودات تنتظر المراجعة / Brouillons en attente</h2>
        {data.pending_drafts.length === 0 ? (
          <p className="rounded-xl bg-white p-6 text-slate-500 shadow-sm">لا مسودات / Aucun brouillon</p>
        ) : (
          <div className="space-y-2">
            {data.pending_drafts.map((d) => (
              <Link
                key={d.id}
                href={`/admin/content/${d.id}/edit`}
                className="flex items-center justify-between rounded-xl bg-white p-4 shadow-sm hover:shadow-md"
              >
                <span dir="auto">
                  {d.title_ar} / {d.title_fr}
                </span>
                <span className="flex gap-2 text-xs">
                  {d.is_ai_generated && (
                    <span className="rounded bg-purple-100 px-2 py-0.5 font-semibold text-purple-700">🤖 AI</span>
                  )}
                  <span className="rounded bg-amber-100 px-2 py-0.5 font-semibold text-warning">{d.type}</span>
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold">آخر نشاط / Activité récente</h2>
        <div className="space-y-2">
          {data.recent_activity.map((c) => (
            <div key={c.id} className="flex items-center justify-between rounded-xl bg-white p-4 shadow-sm">
              <span dir="auto">
                {c.title_ar} / {c.title_fr}
              </span>
              <span
                className={`rounded px-2 py-0.5 text-xs font-semibold ${
                  c.status === "published" ? "bg-emerald-100 text-success" : "bg-amber-100 text-warning"
                }`}
              >
                {c.status === "published" ? "منشور / Publié" : "مسودة / Brouillon"}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
