"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";
import type { ContentSummary } from "@/lib/types";

const TYPE_LABELS: Record<string, string> = {
  course: "دورة / Formation",
  lesson: "درس / Leçon",
  quiz: "كويز / Quiz",
  exercise: "تمرين / Exercice",
};

export default function AdminContentList() {
  const [items, setItems] = useState<ContentSummary[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    const params = new URLSearchParams();
    if (statusFilter) params.set("status", statusFilter);
    if (typeFilter) params.set("type", typeFilter);
    api<ContentSummary[]>(`/api/admin/content?${params}`).then(setItems).catch((e) => setError(e.message));
  }, [statusFilter, typeFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const publish = async (id: string) => {
    await api(`/api/admin/content/${id}/publish`, { method: "POST" });
    load();
  };

  const remove = async (id: string) => {
    if (!confirm("حذف المحتوى نهائياً؟ / Supprimer définitivement ?")) return;
    await api(`/api/admin/content/${id}`, { method: "DELETE" });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">المحتويات / Contenus</h1>
        <Link
          href="/admin/content/new"
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        >
          ➕ إضافة محتوى / Ajouter
        </Link>
      </div>

      <div className="flex flex-wrap gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">كل الحالات / Tous statuts</option>
          <option value="draft">مسودة / Brouillon</option>
          <option value="published">منشور / Publié</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">كل الأنواع / Tous types</option>
          <option value="course">دورة / Formation</option>
          <option value="lesson">درس / Leçon</option>
          <option value="quiz">كويز / Quiz</option>
          <option value="exercise">تمرين / Exercice</option>
        </select>
      </div>

      {error && <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>}

      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-white p-4 shadow-sm">
            <div className="min-w-0">
              <p dir="auto" className="font-semibold">
                {item.title_ar} / {item.title_fr}
              </p>
              <p className="mt-1 flex gap-2 text-xs">
                <span className="rounded bg-blue-50 px-2 py-0.5 font-semibold text-primary">
                  {TYPE_LABELS[item.type]}
                </span>
                <span
                  className={`rounded px-2 py-0.5 font-semibold ${
                    item.status === "published" ? "bg-emerald-100 text-success" : "bg-amber-100 text-warning"
                  }`}
                >
                  {item.status === "published" ? "منشور / Publié" : "مسودة / Brouillon"}
                </span>
                {item.is_ai_generated && (
                  <span className="rounded bg-purple-100 px-2 py-0.5 font-semibold text-purple-700">🤖 AI</span>
                )}
              </p>
            </div>
            <div className="flex gap-2">
              <Link
                href={`/admin/content/${item.id}/edit`}
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
              >
                تعديل / Modifier
              </Link>
              {item.status === "draft" && (
                <BilingualButton ar="نشر" fr="Publier" variant="success" onClick={() => publish(item.id)} />
              )}
              <BilingualButton ar="حذف" fr="Supprimer" variant="danger" onClick={() => remove(item.id)} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
