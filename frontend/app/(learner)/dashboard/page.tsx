"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ProgressBar from "@/components/progress/ProgressBar";
import { api } from "@/lib/api";
import type { ContentSummary } from "@/lib/types";

interface Dashboard {
  my_contents: ContentSummary[];
  recents: ContentSummary[];
  by_category: {
    category: { id: string; name_ar: string; name_fr: string };
    items: ContentSummary[];
  }[];
}

const TYPE_LABELS: Record<string, string> = {
  course: "دورة / Formation",
  lesson: "درس / Leçon",
  quiz: "كويز / Quiz",
  exercise: "تمرين / Exercice",
};

function ContentCard({ item }: { item: ContentSummary }) {
  const href = item.type === "course" ? `/course/${item.id}` : `/course/${item.id}`;
  return (
    <Link
      href={href}
      className="block w-64 shrink-0 space-y-2 rounded-xl bg-white p-4 shadow-sm transition hover:shadow-md"
    >
      <span className="inline-block rounded bg-blue-50 px-2 py-0.5 text-xs font-semibold text-primary">
        {TYPE_LABELS[item.type]}
      </span>
      <h3 dir="auto" className="line-clamp-2 font-bold">
        {item.title_ar}
      </h3>
      <p dir="auto" className="line-clamp-1 text-sm text-slate-500">
        {item.title_fr}
      </p>
      {item.progress != null && <ProgressBar value={item.progress} />}
    </Link>
  );
}

function Rail({ title, items }: { title: string; items: ContentSummary[] }) {
  if (items.length === 0) return null;
  return (
    <section className="space-y-3">
      <h2 className="text-lg font-bold">{title}</h2>
      <div className="flex gap-4 overflow-x-auto pb-2">
        {items.map((i) => (
          <ContentCard key={i.id} item={i} />
        ))}
      </div>
    </section>
  );
}

export default function LearnerDashboard() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Dashboard>("/api/learner/dashboard").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>;
  if (!data) return <p className="text-slate-500">جارٍ التحميل / Chargement...</p>;

  return (
    <div className="space-y-8">
      <Rail title="محتوياتي / Mes contenus" items={data.my_contents} />
      <Rail title="الأحدث / Récents" items={data.recents} />
      {data.by_category.map((c) => (
        <Rail
          key={c.category.id}
          title={`${c.category.name_ar} / ${c.category.name_fr}`}
          items={c.items}
        />
      ))}
    </div>
  );
}
