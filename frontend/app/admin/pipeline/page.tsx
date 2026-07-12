"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";
import type { PipelineJob } from "@/lib/types";

const STATUS_LABELS: Record<PipelineJob["status"], string> = {
  pending: "قيد الانتظار / En attente",
  validating: "تقييم الطلب / Validation...",
  searching: "البحث جارٍ / Recherche en cours...",
  analyzing: "التحليل جارٍ / Analyse en cours...",
  awaiting_user: "بانتظار اختيارك / En attente de votre choix",
  generating: "التوليد جارٍ / Génération en cours...",
  uploading: "الرفع جارٍ / Téléversement...",
  done: "مكتمل / Terminé ✓",
  failed: "فشل / Échec ✗",
};

const ERROR_LABELS: Record<string, string> = {
  prompt_unclear: "الطلب غير واضح — أعد الصياغة / Prompt peu clair — reformulez",
  connection_error: "Failed — تعذّر الاتصال / Connexion impossible",
  generation_error: "فشل التوليد / Échec de la génération",
};

function statusColor(status: PipelineJob["status"]) {
  if (status === "done") return "bg-emerald-100 text-success";
  if (status === "failed") return "bg-red-100 text-danger";
  if (status === "awaiting_user") return "bg-amber-100 text-warning";
  return "bg-blue-100 text-primary";
}

function JobCard({ job, onRefresh }: { job: PipelineJob; onRefresh: () => void }) {
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const answer = async () => {
    const contents = job.user_request?.possible_contents.filter((_, i) => selected.has(i)) ?? [];
    await api(`/api/admin/pipeline/${job.id}/answer`, {
      method: "POST",
      body: JSON.stringify({ selected_contents: contents }),
    });
    onRefresh();
  };

  return (
    <div className="space-y-3 rounded-xl bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p dir="auto" className="font-semibold">
          {job.prompt}
        </p>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusColor(job.status)}`}>
          {STATUS_LABELS[job.status]}
        </span>
      </div>

      {job.status === "failed" && job.error_message && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-danger">
          {ERROR_LABELS[job.error_message] ?? job.error_message}
        </p>
      )}

      {/* R3 — اختيار المحتويات المطلوب إنشاؤها */}
      {job.status === "awaiting_user" && job.user_request && (
        <div className="space-y-3">
          {job.user_request.duplicate_warnings.length > 0 && (
            <div className="rounded-lg bg-amber-50 p-3 text-sm text-warning">
              ⚠️ محتوى مشابه موجود / Contenu similaire existant:
              <ul className="mt-1 list-disc ps-5">
                {job.user_request.duplicate_warnings.map((w, i) => (
                  <li key={i} dir="auto">
                    {w.topic} ≈ {w.existing_title} ({w.similarity}%)
                  </li>
                ))}
              </ul>
            </div>
          )}
          <p className="text-sm font-semibold">اختر المحتويات المطلوب إنشاؤها / Sélectionnez les contenus à créer:</p>
          <div className="space-y-2">
            {job.user_request.possible_contents.map((c, i) => (
              <label key={i} className="flex items-start gap-2 rounded-lg border border-slate-200 p-3 text-sm">
                <input
                  type="checkbox"
                  checked={selected.has(i)}
                  onChange={(e) => {
                    const next = new Set(selected);
                    if (e.target.checked) next.add(i);
                    else next.delete(i);
                    setSelected(next);
                  }}
                />
                <span dir="auto">
                  <span className="rounded bg-blue-50 px-1.5 py-0.5 text-xs font-semibold text-primary">{c.type}</span>{" "}
                  <strong>{c.title_ar} / {c.title_fr}</strong>
                  <br />
                  <span className="text-slate-500">{c.description}</span>
                </span>
              </label>
            ))}
          </div>
          <BilingualButton ar="توليد المختار" fr="Générer" variant="success" disabled={selected.size === 0} onClick={answer} />
        </div>
      )}

      {job.status === "done" && job.generated_content_ids && (
        <p className="text-sm">
          ✓ أُنشئت {job.generated_content_ids.length} مسودة —{" "}
          <Link href="/admin/content/drafts" className="font-semibold text-primary hover:underline">
            مراجعة المسودات / Réviser les brouillons
          </Link>
        </p>
      )}
    </div>
  );
}

export default function PipelinePage() {
  const [jobs, setJobs] = useState<PipelineJob[]>([]);
  const [prompt, setPrompt] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(() => {
    api<PipelineJob[]>("/api/admin/pipeline").then(setJobs).catch((e) => setError(e.message));
  }, []);

  // تتبع الحالة real-time — polling كل 3 ثوانٍ ما دامت هناك مهام نشطة
  useEffect(() => {
    load();
    pollRef.current = setInterval(load, 3000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [load]);

  const start = async () => {
    if (!prompt.trim()) return;
    setStarting(true);
    setError(null);
    try {
      await api("/api/admin/pipeline/start", { method: "POST", body: JSON.stringify({ prompt }) });
      setPrompt("");
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطأ / Erreur");
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">AI Pipeline 🤖</h1>

      {/* I1 — كتابة الـ Prompt */}
      <div className="space-y-3 rounded-xl bg-white p-6 shadow-sm">
        <label className="block text-sm font-semibold">
          اكتب طلبك / Écrivez votre demande:
        </label>
        <textarea
          dir="auto"
          rows={3}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none"
          placeholder='مثال: "ابحث عن مواد تعليمية حول السلامة والصحة المهنية بالفرنسية"'
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <BilingualButton ar="إطلاق" fr="Lancer" icon="🚀" disabled={starting || !prompt.trim()} onClick={start} />
      </div>

      {error && <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>}

      <div className="space-y-4">
        {jobs.map((j) => (
          <JobCard key={j.id} job={j} onRefresh={load} />
        ))}
        {jobs.length === 0 && (
          <p className="rounded-xl bg-white p-8 text-center text-slate-500 shadow-sm">
            لا مهام بعد — اكتب Prompt لبدء أول مهمة / Aucune tâche — lancez votre premier prompt
          </p>
        )}
      </div>
    </div>
  );
}
