"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Analytics {
  most_viewed: { id: string; title_ar: string; title_fr: string; views: number }[];
  completion_rates: { course_id: string; title_ar: string; title_fr: string; started: number; completed: number; rate: number }[];
  certificates: { attendance: number; competency: number };
  by_category: { id: string; name_ar: string; name_fr: string; count: number }[];
}

export default function AnalyticsPage() {
  const [data, setData] = useState<Analytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Analytics>("/api/admin/analytics").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>;
  if (!data) return <p className="text-slate-500">جارٍ التحميل / Chargement...</p>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">التحليلات / Analytique</h1>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-3xl font-bold text-primary">{data.certificates.attendance}</p>
          <p className="mt-1 text-sm text-slate-500">شهادات حضورية / Certificats de présence</p>
        </div>
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <p className="text-3xl font-bold text-success">{data.certificates.competency}</p>
          <p className="mt-1 text-sm text-slate-500">شهادات كفاءة / Certificats de compétence</p>
        </div>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-bold">الأكثر مشاهدة / Les plus consultés</h2>
        <div className="space-y-2">
          {data.most_viewed.map((m) => (
            <div key={m.id} className="flex justify-between rounded-xl bg-white p-4 shadow-sm">
              <span dir="auto">
                {m.title_ar} / {m.title_fr}
              </span>
              <span className="font-bold text-primary">{m.views}</span>
            </div>
          ))}
          {data.most_viewed.length === 0 && (
            <p className="rounded-xl bg-white p-6 text-slate-500 shadow-sm">لا بيانات بعد / Pas encore de données</p>
          )}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold">نسب إكمال الدورات / Taux de complétion</h2>
        <div className="space-y-2">
          {data.completion_rates.map((c) => (
            <div key={c.course_id} className="space-y-2 rounded-xl bg-white p-4 shadow-sm">
              <div className="flex justify-between">
                <span dir="auto">
                  {c.title_ar} / {c.title_fr}
                </span>
                <span className="text-sm text-slate-500">
                  {c.completed}/{c.started} — {c.rate}%
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full bg-success" style={{ width: `${c.rate}%` }} />
              </div>
            </div>
          ))}
          {data.completion_rates.length === 0 && (
            <p className="rounded-xl bg-white p-6 text-slate-500 shadow-sm">لا دورات منشورة / Aucune formation publiée</p>
          )}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold">التوزيع بالفئة / Répartition par catégorie</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.by_category.map((c) => (
            <div key={c.id} className="rounded-xl bg-white p-4 shadow-sm">
              <p dir="auto" className="text-sm">
                {c.name_ar} / {c.name_fr}
              </p>
              <p className="mt-1 text-2xl font-bold text-primary">{c.count}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
