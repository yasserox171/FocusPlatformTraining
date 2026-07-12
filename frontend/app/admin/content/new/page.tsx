"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";

interface QuizQuestionForm {
  question_text: string;
  question_type: "mcq" | "yes_no";
  options: { id: string; text: string; is_correct: boolean }[];
  hint: string;
  is_final_quiz: boolean;
}

interface ParagraphForm {
  type: "text" | "video" | "quiz" | "exercise";
  lang_hint: "ar" | "fr" | "auto";
  content_html: string;
  video_url: string;
  video_type: "youtube" | "direct";
  quiz_questions: QuizQuestionForm[];
  exercise: { description: string; solution: string; hint: string };
}

interface LessonForm {
  title_ar: string;
  title_fr: string;
  paragraphs: ParagraphForm[];
}

interface UnitForm {
  title_ar: string;
  title_fr: string;
  prerequisite_unit_order: number | null;
  lessons: LessonForm[];
}

const emptyParagraph = (): ParagraphForm => ({
  type: "text",
  lang_hint: "auto",
  content_html: "",
  video_url: "",
  video_type: "youtube",
  quiz_questions: [],
  exercise: { description: "", solution: "", hint: "" },
});

const emptyLesson = (): LessonForm => ({ title_ar: "", title_fr: "", paragraphs: [emptyParagraph()] });
const emptyUnit = (): UnitForm => ({
  title_ar: "",
  title_fr: "",
  prerequisite_unit_order: null,
  lessons: [emptyLesson()],
});

const input = "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none";

function QuizEditor({
  question,
  onChange,
  onRemove,
}: {
  question: QuizQuestionForm;
  onChange: (q: QuizQuestionForm) => void;
  onRemove: () => void;
}) {
  const setYesNo = (isYesNo: boolean) => {
    onChange({
      ...question,
      question_type: isYesNo ? "yes_no" : "mcq",
      options: isYesNo
        ? [
            { id: "yes", text: "نعم / Oui", is_correct: true },
            { id: "no", text: "لا / Non", is_correct: false },
          ]
        : question.options,
    });
  };
  return (
    <div className="space-y-2 rounded-lg border border-slate-200 p-3">
      <div className="flex gap-2">
        <input
          dir="auto"
          className={input}
          placeholder="السؤال / Question"
          value={question.question_text}
          onChange={(e) => onChange({ ...question, question_text: e.target.value })}
        />
        <select
          className="rounded-lg border border-slate-300 px-2 text-sm"
          value={question.question_type}
          onChange={(e) => setYesNo(e.target.value === "yes_no")}
        >
          <option value="mcq">MCQ</option>
          <option value="yes_no">نعم/لا / Oui-Non</option>
        </select>
        <button onClick={onRemove} className="text-danger">
          ✕
        </button>
      </div>
      {question.options.map((o, i) => (
        <div key={i} className="flex items-center gap-2">
          <input
            type="radio"
            name={`correct-${question.question_text}-${i}`}
            checked={o.is_correct}
            onChange={() =>
              onChange({
                ...question,
                options: question.options.map((op, j) => ({ ...op, is_correct: j === i })),
              })
            }
          />
          <input
            dir="auto"
            className={input}
            placeholder={`خيار ${i + 1} / Option ${i + 1}`}
            value={o.text}
            onChange={(e) =>
              onChange({
                ...question,
                options: question.options.map((op, j) => (j === i ? { ...op, text: e.target.value } : op)),
              })
            }
          />
        </div>
      ))}
      {question.question_type === "mcq" && (
        <button
          className="text-sm text-primary"
          onClick={() =>
            onChange({
              ...question,
              options: [
                ...question.options,
                { id: String.fromCharCode(97 + question.options.length), text: "", is_correct: false },
              ],
            })
          }
        >
          ➕ خيار / Option
        </button>
      )}
      <input
        dir="auto"
        className={input}
        placeholder="تلميح (اختياري) / Indice (optionnel)"
        value={question.hint}
        onChange={(e) => onChange({ ...question, hint: e.target.value })}
      />
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={question.is_final_quiz}
          onChange={(e) => onChange({ ...question, is_final_quiz: e.target.checked })}
        />
        الكويز النهائي / Quiz final
      </label>
    </div>
  );
}

function ParagraphEditor({
  paragraph,
  onChange,
  onRemove,
}: {
  paragraph: ParagraphForm;
  onChange: (p: ParagraphForm) => void;
  onRemove: () => void;
}) {
  return (
    <div className="space-y-2 rounded-lg bg-surface p-3">
      <div className="flex items-center gap-2">
        <select
          className="rounded-lg border border-slate-300 px-2 py-1 text-sm"
          value={paragraph.type}
          onChange={(e) => onChange({ ...paragraph, type: e.target.value as ParagraphForm["type"] })}
        >
          <option value="text">نص / Texte</option>
          <option value="video">فيديو / Vidéo</option>
          <option value="quiz">كويز / Quiz</option>
          <option value="exercise">تمرين / Exercice</option>
        </select>
        <select
          className="rounded-lg border border-slate-300 px-2 py-1 text-sm"
          value={paragraph.lang_hint}
          onChange={(e) => onChange({ ...paragraph, lang_hint: e.target.value as ParagraphForm["lang_hint"] })}
        >
          <option value="auto">Auto</option>
          <option value="ar">AR</option>
          <option value="fr">FR</option>
        </select>
        <button onClick={onRemove} className="mr-auto text-danger">
          ✕ حذف / Suppr.
        </button>
      </div>

      {paragraph.type === "text" && (
        <textarea
          dir="auto"
          rows={4}
          className={input}
          placeholder="<p>المحتوى HTML / Contenu HTML</p>"
          value={paragraph.content_html}
          onChange={(e) => onChange({ ...paragraph, content_html: e.target.value })}
        />
      )}

      {paragraph.type === "video" && (
        <div className="flex gap-2">
          <input
            dir="ltr"
            className={input}
            placeholder="https://youtube.com/watch?v=..."
            value={paragraph.video_url}
            onChange={(e) => onChange({ ...paragraph, video_url: e.target.value })}
          />
          <select
            className="rounded-lg border border-slate-300 px-2 text-sm"
            value={paragraph.video_type}
            onChange={(e) => onChange({ ...paragraph, video_type: e.target.value as "youtube" | "direct" })}
          >
            <option value="youtube">YouTube</option>
            <option value="direct">رابط مباشر / Lien direct</option>
          </select>
        </div>
      )}

      {paragraph.type === "quiz" && (
        <div className="space-y-2">
          {paragraph.quiz_questions.map((q, i) => (
            <QuizEditor
              key={i}
              question={q}
              onChange={(nq) =>
                onChange({
                  ...paragraph,
                  quiz_questions: paragraph.quiz_questions.map((x, j) => (j === i ? nq : x)),
                })
              }
              onRemove={() =>
                onChange({
                  ...paragraph,
                  quiz_questions: paragraph.quiz_questions.filter((_, j) => j !== i),
                })
              }
            />
          ))}
          <button
            className="text-sm text-primary"
            onClick={() =>
              onChange({
                ...paragraph,
                quiz_questions: [
                  ...paragraph.quiz_questions,
                  {
                    question_text: "",
                    question_type: "mcq",
                    options: [
                      { id: "a", text: "", is_correct: true },
                      { id: "b", text: "", is_correct: false },
                    ],
                    hint: "",
                    is_final_quiz: false,
                  },
                ],
              })
            }
          >
            ➕ سؤال / Question
          </button>
        </div>
      )}

      {paragraph.type === "exercise" && (
        <div className="space-y-2">
          <textarea
            dir="auto"
            rows={2}
            className={input}
            placeholder="نص التمرين / Énoncé de l'exercice"
            value={paragraph.exercise.description}
            onChange={(e) =>
              onChange({ ...paragraph, exercise: { ...paragraph.exercise, description: e.target.value } })
            }
          />
          <textarea
            dir="auto"
            rows={2}
            className={input}
            placeholder="الحل الكامل / Solution complète"
            value={paragraph.exercise.solution}
            onChange={(e) =>
              onChange({ ...paragraph, exercise: { ...paragraph.exercise, solution: e.target.value } })
            }
          />
          <input
            dir="auto"
            className={input}
            placeholder="تلميح (اختياري) / Indice (optionnel)"
            value={paragraph.exercise.hint}
            onChange={(e) =>
              onChange({ ...paragraph, exercise: { ...paragraph.exercise, hint: e.target.value } })
            }
          />
        </div>
      )}
    </div>
  );
}

function LessonEditor({
  lesson,
  onChange,
  onRemove,
}: {
  lesson: LessonForm;
  onChange: (l: LessonForm) => void;
  onRemove: () => void;
}) {
  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex gap-2">
        <input
          dir="rtl"
          className={input}
          placeholder="عنوان الدرس بالعربية"
          value={lesson.title_ar}
          onChange={(e) => onChange({ ...lesson, title_ar: e.target.value })}
        />
        <input
          dir="ltr"
          className={input}
          placeholder="Titre de la leçon en français"
          value={lesson.title_fr}
          onChange={(e) => onChange({ ...lesson, title_fr: e.target.value })}
        />
        <button onClick={onRemove} className="text-danger">
          ✕
        </button>
      </div>
      {lesson.paragraphs.map((p, i) => (
        <ParagraphEditor
          key={i}
          paragraph={p}
          onChange={(np) => onChange({ ...lesson, paragraphs: lesson.paragraphs.map((x, j) => (j === i ? np : x)) })}
          onRemove={() => onChange({ ...lesson, paragraphs: lesson.paragraphs.filter((_, j) => j !== i) })}
        />
      ))}
      <button
        className="text-sm text-primary"
        onClick={() => onChange({ ...lesson, paragraphs: [...lesson.paragraphs, emptyParagraph()] })}
      >
        ➕ فقرة / Paragraphe
      </button>
    </div>
  );
}

export default function NewContentPage() {
  const router = useRouter();
  const [type, setType] = useState<"course" | "lesson" | "quiz" | "exercise">("lesson");
  const [titleAr, setTitleAr] = useState("");
  const [titleFr, setTitleFr] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [passThreshold, setPassThreshold] = useState(35);
  const [durationHours, setDurationHours] = useState(0);
  const [categories, setCategories] = useState<{ id: string; name_ar: string; name_fr: string }[]>([]);
  const [units, setUnits] = useState<UnitForm[]>([emptyUnit()]);
  const [lessons, setLessons] = useState<LessonForm[]>([emptyLesson()]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api<typeof categories>("/api/admin/content/categories").then(setCategories).catch(() => {});
  }, []);

  const serializeLesson = (l: LessonForm, order: number) => ({
    title_ar: l.title_ar,
    title_fr: l.title_fr,
    order,
    paragraphs: l.paragraphs.map((p, i) => ({
      type: p.type,
      order: i,
      lang_hint: p.lang_hint,
      content_html: p.type === "text" ? p.content_html : null,
      video_url: p.type === "video" ? p.video_url : null,
      video_type: p.type === "video" ? p.video_type : null,
      quiz_questions:
        p.type === "quiz"
          ? p.quiz_questions.map((q) => ({ ...q, hint: q.hint || null }))
          : [],
      exercises:
        p.type === "exercise"
          ? [{ ...p.exercise, hint: p.exercise.hint || null }]
          : [],
    })),
  });

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      await api("/api/admin/content", {
        method: "POST",
        body: JSON.stringify({
          type,
          title_ar: titleAr,
          title_fr: titleFr,
          category_id: categoryId || null,
          pass_threshold: passThreshold,
          duration_hours: durationHours,
          units:
            type === "course"
              ? units.map((u, i) => ({
                  title_ar: u.title_ar,
                  title_fr: u.title_fr,
                  order: i,
                  prerequisite_unit_order: u.prerequisite_unit_order,
                  lessons: u.lessons.map(serializeLesson),
                }))
              : [],
          lessons: type !== "course" ? lessons.map(serializeLesson) : [],
        }),
      });
      router.push("/admin/content");
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطأ / Erreur");
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      <h1 className="text-2xl font-bold">إضافة محتوى / Ajouter un contenu</h1>

      <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
        <div className="grid gap-3 sm:grid-cols-2">
          <select className={input} value={type} onChange={(e) => setType(e.target.value as typeof type)}>
            <option value="lesson">درس / Leçon</option>
            <option value="course">دورة تكوينية / Formation</option>
            <option value="quiz">كويز / Quiz</option>
            <option value="exercise">تمرين / Exercice</option>
          </select>
          <select className={input} value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">بدون فئة / Sans catégorie</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name_ar} / {c.name_fr}
              </option>
            ))}
          </select>
          <input dir="rtl" className={input} placeholder="العنوان بالعربية" value={titleAr} onChange={(e) => setTitleAr(e.target.value)} />
          <input dir="ltr" className={input} placeholder="Titre en français" value={titleFr} onChange={(e) => setTitleFr(e.target.value)} />
        </div>
        {type === "course" && (
          <div className="flex flex-wrap gap-6">
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
            <label className="block text-sm">
              مدة التكوين بالساعات / Durée (heures) — تظهر على الشهادة
              <input
                type="number"
                min={0}
                className={`${input} mt-1 w-32`}
                value={durationHours}
                onChange={(e) => setDurationHours(Number(e.target.value))}
              />
            </label>
          </div>
        )}
      </div>

      {type === "course" ? (
        <div className="space-y-4">
          {units.map((u, i) => (
            <div key={i} className="space-y-3 rounded-xl bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2">
                <span className="font-bold">وحدة / Unité {i + 1}</span>
                <button onClick={() => setUnits(units.filter((_, j) => j !== i))} className="mr-auto text-danger">
                  ✕
                </button>
              </div>
              <div className="grid gap-2 sm:grid-cols-2">
                <input
                  dir="rtl"
                  className={input}
                  placeholder="عنوان الوحدة بالعربية"
                  value={u.title_ar}
                  onChange={(e) => setUnits(units.map((x, j) => (j === i ? { ...x, title_ar: e.target.value } : x)))}
                />
                <input
                  dir="ltr"
                  className={input}
                  placeholder="Titre de l'unité en français"
                  value={u.title_fr}
                  onChange={(e) => setUnits(units.map((x, j) => (j === i ? { ...x, title_fr: e.target.value } : x)))}
                />
              </div>
              <label className="block text-sm">
                Prerequisite — الوحدة المطلوب إكمالها قبل هذه:
                <select
                  className={`${input} mt-1`}
                  value={u.prerequisite_unit_order ?? ""}
                  onChange={(e) =>
                    setUnits(
                      units.map((x, j) =>
                        j === i
                          ? { ...x, prerequisite_unit_order: e.target.value === "" ? null : Number(e.target.value) }
                          : x
                      )
                    )
                  }
                >
                  <option value="">بدون / Aucune</option>
                  {units.map(
                    (_, j) =>
                      j !== i && (
                        <option key={j} value={j}>
                          وحدة / Unité {j + 1}
                        </option>
                      )
                  )}
                </select>
              </label>
              {u.lessons.map((l, li) => (
                <LessonEditor
                  key={li}
                  lesson={l}
                  onChange={(nl) =>
                    setUnits(units.map((x, j) => (j === i ? { ...x, lessons: x.lessons.map((y, k) => (k === li ? nl : y)) } : x)))
                  }
                  onRemove={() =>
                    setUnits(units.map((x, j) => (j === i ? { ...x, lessons: x.lessons.filter((_, k) => k !== li) } : x)))
                  }
                />
              ))}
              <button
                className="text-sm text-primary"
                onClick={() => setUnits(units.map((x, j) => (j === i ? { ...x, lessons: [...x.lessons, emptyLesson()] } : x)))}
              >
                ➕ درس / Leçon
              </button>
            </div>
          ))}
          <button className="text-sm font-semibold text-primary" onClick={() => setUnits([...units, emptyUnit()])}>
            ➕ وحدة / Unité
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {lessons.map((l, i) => (
            <LessonEditor
              key={i}
              lesson={l}
              onChange={(nl) => setLessons(lessons.map((x, j) => (j === i ? nl : x)))}
              onRemove={() => setLessons(lessons.filter((_, j) => j !== i))}
            />
          ))}
        </div>
      )}

      {error && <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>}
      <div className="flex gap-3">
        <BilingualButton ar="حفظ كمسودة" fr="Enregistrer" variant="primary" disabled={saving} onClick={save} />
      </div>
    </div>
  );
}
