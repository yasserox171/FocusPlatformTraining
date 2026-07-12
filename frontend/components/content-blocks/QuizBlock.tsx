"use client";

import { useState } from "react";
import LangBadge from "./LangBadge";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";
import type { Paragraph, QuizQuestion } from "@/lib/types";

function QuestionCard({ question }: { question: QuizQuestion }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [correctIds, setCorrectIds] = useState<string[] | null>(null);

  const reveal = async () => {
    const data = await api<{ correct_option_ids: string[] }>(
      `/api/learner/quiz/${question.id}/answer`
    );
    setCorrectIds(data.correct_option_ids);
  };

  const optionClass = (id: string) => {
    if (correctIds) {
      if (correctIds.includes(id)) return "border-success bg-emerald-50 text-success";
      if (selected === id) return "border-danger bg-red-50 text-danger";
      return "border-slate-200";
    }
    return selected === id
      ? "border-primary bg-blue-50"
      : "border-slate-200 hover:border-primary";
  };

  return (
    <div className="space-y-3">
      <p dir="auto" className="font-semibold">
        {question.question_text}
      </p>
      <div className="space-y-2">
        {question.options.map((o) => (
          <button
            key={o.id}
            dir="auto"
            onClick={() => !correctIds && setSelected(o.id)}
            className={`block w-full rounded-lg border-2 px-4 py-2 text-start transition ${optionClass(o.id)}`}
          >
            {o.text}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {question.hint && (
          <BilingualButton ar="تلميح" fr="Indice" icon="💡" variant="outline" onClick={() => setShowHint(true)} />
        )}
        <BilingualButton ar="الجواب الصحيح" fr="Bonne réponse" icon="✓" variant="success" onClick={reveal} />
      </div>
      {showHint && question.hint && (
        <p dir="auto" className="rounded-lg bg-amber-50 p-3 text-sm text-warning">
          💡 {question.hint}
        </p>
      )}
    </div>
  );
}

export default function QuizBlock({ paragraph }: { paragraph: Paragraph }) {
  return (
    <div className="relative space-y-6 rounded-xl bg-white p-6 shadow-sm">
      <LangBadge lang={paragraph.lang_hint} />
      {paragraph.quiz_questions.map((q) => (
        <QuestionCard key={q.id} question={q} />
      ))}
    </div>
  );
}
