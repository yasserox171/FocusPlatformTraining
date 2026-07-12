"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";

interface Detail {
  id: string;
  type: string;
  title_ar: string;
  title_fr: string;
  category_id: string | null;
  status: "draft" | "published";
  is_ai_generated: boolean;
  pass_threshold: number;
  units: {
    id: string;
    title_ar: string;
    title_fr: string;
    lessons: { id: string; title_ar: string; title_fr: string; paragraphs: { id: string; type: string; content_html: string | null }[] }[];
  }[];
  lessons: { id: string; title_ar: string; title_fr: string; paragraphs: { id: string; type: string; content_html: string | null }[] }[];
}

const input = "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none";

export default function EditContentPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [item, setItem] = useState<Detail | null>(null);
  const [titleAr, setTitleAr] = useState("");
  const [titleFr, setTitleFr] = useState("");
  const [passThreshold, setPassThreshold] = useState(35);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api<Detail>(`/api/admin/content/${id}`)
      .then((d) => {
        setItem(d);
        setTitleAr(d.title_ar);
        setTitleFr(d.title_fr);
        setPassThreshold(d.pass_threshold);
      })
      .catch((e) => setError(e.message));
  }, [id]);

  const save = async () => {
    setError(null);
    setSaved(false);
    try {
      await api(`/api/admin/content/${id}`, {
        method: "PUT",
        body: JSON.stringify({ title_ar: titleAr, title_fr: titleFr, pass_threshold: passThreshold }),
      });
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطأ / Erreur");
    }
  };

  const publish = async () => {
    await api(`/api/admin/content/${id}/publish`, { method: "POST" });
    router.push("/admin/content");
  };

  if (error && !item) return <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>;
  if (!item) return <p className="text-slate-500">جارٍ التحميل / Chargement...</p>;

  const lessonGroups = [
    ...item.units.flatMap((u) => u.lessons.map((l) => ({ ...l, unitTitle: `${u.title_ar} / ${u.title_fr}` }))),
    ...item.lessons.map((l) => ({ ...l, unitTitle: null as string | null })),
  ];

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">تعديل المحتوى / Modifier le contenu</h1>
        {item.status === "draft" && <BilingualButton ar="نشر" fr="Publier" variant="success" onClick={publish} />}
      </div>

      <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
        <div className="flex gap-2 text-xs">
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
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <input dir="rtl" className={input} value={titleAr} onChange={(e) => setTitleAr(e.target.value)} />
          <input dir="ltr" className={input} value={titleFr} onChange={(e) => setTitleFr(e.target.value)} />
        </div>
        {item.type === "course" && (
          <label className="block text-sm">
            نسبة نجاح الكويز النهائي / Seuil de réussite (%)
            <input
              type="number"
              min={0}
              max={100}
              className={`${input} mt-1 w-32`}
              value={passThreshold}
              onChange={(e) => setPassThreshold(Number(e.target.value))}
            />
          </label>
        )}
        {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-danger">{error}</p>}
        {saved && <p className="rounded-lg bg-emerald-50 p-3 text-sm text-success">✓ تم الحفظ / Enregistré</p>}
        <BilingualButton ar="حفظ" fr="Enregistrer" onClick={save} />
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-bold">المعاينة / Aperçu</h2>
        {lessonGroups.map((l) => (
          <div key={l.id} className="space-y-2 rounded-xl bg-white p-4 shadow-sm">
            {l.unitTitle && <p className="text-xs font-semibold text-slate-400">{l.unitTitle}</p>}
            <p dir="auto" className="font-bold">
              {l.title_ar} / {l.title_fr}
            </p>
            {l.paragraphs.map((p) => (
              <div key={p.id} className="rounded-lg bg-surface p-3 text-sm">
                <span className="text-xs font-semibold text-slate-400">{p.type}</span>
                {p.content_html && (
                  <div dir="auto" className="content-html mt-1" dangerouslySetInnerHTML={{ __html: p.content_html }} />
                )}
              </div>
            ))}
          </div>
        ))}
      </section>
    </div>
  );
}
