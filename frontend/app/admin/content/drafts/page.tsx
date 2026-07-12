"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";
import type { ContentSummary } from "@/lib/types";

/** المسودات — محتوى AI أو يدوي في انتظار النشر */
export default function DraftsPage() {
  const [items, setItems] = useState<ContentSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    api<ContentSummary[]>("/api/admin/content?status=draft").then(setItems).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const publish = async (id: string) => {
    await api(`/api/admin/content/${id}/publish`, { method: "POST" });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">المسودات / Brouillons</h1>
      {error && <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>}
      {items.length === 0 ? (
        <p className="rounded-xl bg-white p-8 text-center text-slate-500 shadow-sm">
          لا مسودات / Aucun brouillon
        </p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-white p-4 shadow-sm">
              <div>
                <p dir="auto" className="font-semibold">
                  {item.title_ar} / {item.title_fr}
                </p>
                {item.is_ai_generated && (
                  <span className="mt-1 inline-block rounded bg-purple-100 px-2 py-0.5 text-xs font-semibold text-purple-700">
                    🤖 مولّد بالذكاء الاصطناعي / Généré par IA
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <Link
                  href={`/admin/content/${item.id}/edit`}
                  className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
                >
                  مراجعة / Réviser
                </Link>
                <BilingualButton ar="نشر" fr="Publier" variant="success" onClick={() => publish(item.id)} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
