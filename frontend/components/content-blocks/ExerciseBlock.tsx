"use client";

import { useState } from "react";
import LangBadge from "./LangBadge";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";
import type { Paragraph } from "@/lib/types";

/** كتلة التمرين — لا تقييم أبداً: عرض + تلميح + حل مخفي حتى الضغط */
export default function ExerciseBlock({ paragraph }: { paragraph: Paragraph }) {
  return (
    <div className="relative space-y-6 rounded-xl bg-white p-6 shadow-sm">
      <LangBadge lang={paragraph.lang_hint} />
      {paragraph.exercises.map((ex) => (
        <ExerciseCard key={ex.id} id={ex.id} description={ex.description} hint={ex.hint} />
      ))}
    </div>
  );
}

function ExerciseCard({
  id,
  description,
  hint,
}: {
  id: string;
  description: string;
  hint: string | null;
}) {
  const [showHint, setShowHint] = useState(false);
  const [solution, setSolution] = useState<string | null>(null);

  const revealSolution = async () => {
    const data = await api<{ solution: string }>(`/api/learner/exercise/${id}/solution`);
    setSolution(data.solution);
  };

  return (
    <div className="space-y-3">
      <p dir="auto" className="whitespace-pre-wrap leading-relaxed">
        {description}
      </p>
      <div className="flex flex-wrap gap-2">
        {hint && (
          <BilingualButton ar="تلميح" fr="Indice" icon="💡" variant="outline" onClick={() => setShowHint(true)} />
        )}
        <BilingualButton ar="الحل" fr="Solution" icon="✓" variant="success" onClick={revealSolution} />
      </div>
      {showHint && hint && (
        <p dir="auto" className="rounded-lg bg-amber-50 p-3 text-sm text-warning">
          💡 {hint}
        </p>
      )}
      {solution && (
        <div dir="auto" className="whitespace-pre-wrap rounded-lg bg-emerald-50 p-4 text-sm">
          {solution}
        </div>
      )}
    </div>
  );
}
