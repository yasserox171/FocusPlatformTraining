"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import BilingualButton from "@/components/bilingual/BilingualButton";
import ExerciseBlock from "@/components/content-blocks/ExerciseBlock";
import QuizBlock from "@/components/content-blocks/QuizBlock";
import TextEditorBlock from "@/components/content-blocks/TextEditorBlock";
import VideoBlock from "@/components/content-blocks/VideoBlock";
import ProgressBar from "@/components/progress/ProgressBar";
import { api } from "@/lib/api";
import type { CourseDetail, Lesson, Paragraph } from "@/lib/types";

interface FlatLesson extends Lesson {
  unitId: string | null;
  locked: boolean;
}

export default function CoursePage() {
  const { id } = useParams<{ id: string }>();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);
  const [quizResult, setQuizResult] = useState<{
    score: number;
    passed: boolean;
    message: string;
    certificate_awarded: { serial_number: string } | null;
  } | null>(null);
  const [finalAnswers, setFinalAnswers] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    try {
      const data = await api<CourseDetail>(`/api/learner/course/${id}`);
      setCourse(data);
      setActiveLessonId((prev) => {
        if (prev) return prev;
        const first = data.units.find((u) => u.accessible)?.lessons[0] ?? data.lessons[0];
        return first?.id ?? null;
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطأ / Erreur");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const flatLessons: FlatLesson[] = useMemo(() => {
    if (!course) return [];
    const fromUnits = course.units.flatMap((u) =>
      u.lessons.map((l) => ({ ...l, unitId: u.id, locked: !u.accessible }))
    );
    const standalone = course.lessons.map((l) => ({ ...l, unitId: null, locked: false }));
    return [...fromUnits, ...standalone];
  }, [course]);

  const activeIndex = flatLessons.findIndex((l) => l.id === activeLessonId);
  const activeLesson = activeIndex >= 0 ? flatLessons[activeIndex] : null;

  const finalQuizQuestions = useMemo(
    () =>
      flatLessons.flatMap((l) =>
        l.paragraphs.flatMap((p) => p.quiz_questions.filter((q) => q.is_final_quiz))
      ),
    [flatLessons]
  );

  const markCompleted = async (paragraph: Paragraph) => {
    if (paragraph.completed || !course) return;
    try {
      await api("/api/learner/progress", {
        method: "POST",
        body: JSON.stringify({ content_item_id: course.id, paragraph_id: paragraph.id }),
      });
      await load();
    } catch {
      /* الوحدة مقفلة أو خطأ شبكة */
    }
  };

  const goTo = async (index: number) => {
    const target = flatLessons[index];
    if (!target || target.locked) return;
    // إكمال فقرات الدرس الحالي عند الانتقال
    if (activeLesson) {
      for (const p of activeLesson.paragraphs) await markCompleted(p);
    }
    setActiveLessonId(target.id);
    window.scrollTo({ top: 0 });
  };

  const submitFinalQuiz = async () => {
    if (!course) return;
    const result = await api<typeof quizResult>(`/api/learner/quiz/${course.id}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers: finalAnswers }),
    });
    setQuizResult(result);
  };

  if (error) return <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>;
  if (!course) return <p className="text-slate-500">جارٍ التحميل / Chargement...</p>;

  return (
    <div className="space-y-6">
      <header className="space-y-3 rounded-xl bg-white p-6 shadow-sm">
        <h1 dir="auto" className="text-2xl font-bold">
          {course.title_ar}
        </h1>
        <p dir="auto" className="text-slate-500">
          {course.title_fr}
        </p>
        {course.progress != null && <ProgressBar value={course.progress} />}
      </header>

      <div className="flex flex-col gap-6 lg:flex-row">
        {/* Sidebar — قائمة الوحدات والدروس */}
        <aside className="w-full shrink-0 space-y-4 lg:w-72">
          {course.units.map((unit) => (
            <div key={unit.id} className="rounded-xl bg-white p-4 shadow-sm">
              <p dir="auto" className="mb-2 flex items-center gap-2 font-bold">
                {!unit.accessible && <span title="مقفلة / Verrouillée">🔒</span>}
                {unit.completed && <span className="text-success">✓</span>}
                {unit.title_ar} / {unit.title_fr}
              </p>
              <ul className="space-y-1">
                {unit.lessons.map((lesson) => {
                  const done = lesson.paragraphs.every((p) => p.completed);
                  return (
                    <li key={lesson.id}>
                      <button
                        dir="auto"
                        disabled={!unit.accessible}
                        onClick={() => setActiveLessonId(lesson.id)}
                        className={`w-full rounded-lg px-3 py-1.5 text-start text-sm transition disabled:cursor-not-allowed disabled:opacity-40 ${
                          lesson.id === activeLessonId
                            ? "bg-primary text-white"
                            : "hover:bg-slate-100"
                        }`}
                      >
                        {done ? "✓ " : ""}
                        {lesson.title_ar}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
          {course.lessons.length > 0 && (
            <div className="rounded-xl bg-white p-4 shadow-sm">
              <ul className="space-y-1">
                {course.lessons.map((lesson) => (
                  <li key={lesson.id}>
                    <button
                      dir="auto"
                      onClick={() => setActiveLessonId(lesson.id)}
                      className={`w-full rounded-lg px-3 py-1.5 text-start text-sm ${
                        lesson.id === activeLessonId ? "bg-primary text-white" : "hover:bg-slate-100"
                      }`}
                    >
                      {lesson.title_ar}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>

        {/* منطقة المحتوى — الفقرات بالترتيب */}
        <div className="min-w-0 flex-1 space-y-4">
          {activeLesson ? (
            <>
              <h2 dir="auto" className="text-xl font-bold">
                {activeLesson.title_ar} / {activeLesson.title_fr}
              </h2>
              {activeLesson.paragraphs
                .filter((p) => !p.quiz_questions.some((q) => q.is_final_quiz))
                .map((p) => {
                  switch (p.type) {
                    case "text":
                      return <TextEditorBlock key={p.id} paragraph={p} />;
                    case "video":
                      return <VideoBlock key={p.id} paragraph={p} />;
                    case "quiz":
                      return <QuizBlock key={p.id} paragraph={p} />;
                    case "exercise":
                      return <ExerciseBlock key={p.id} paragraph={p} />;
                  }
                })}
              <div className="flex justify-between pt-2">
                <BilingualButton
                  ar="السابق"
                  fr="Précédent"
                  variant="outline"
                  disabled={activeIndex <= 0}
                  onClick={() => goTo(activeIndex - 1)}
                />
                <BilingualButton
                  ar="التالي"
                  fr="Suivant"
                  disabled={activeIndex >= flatLessons.length - 1}
                  onClick={() => goTo(activeIndex + 1)}
                />
              </div>
            </>
          ) : (
            <p className="text-slate-500">لا دروس بعد / Pas encore de leçons</p>
          )}

          {/* الكويز النهائي / Quiz final */}
          {finalQuizQuestions.length > 0 && (
            <section className="space-y-4 rounded-xl border-2 border-primary/30 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-bold text-primary">الكويز النهائي / Quiz final</h2>
              {finalQuizQuestions.map((q) => (
                <div key={q.id} className="space-y-2">
                  <p dir="auto" className="font-semibold">
                    {q.question_text}
                  </p>
                  {q.options.map((o) => (
                    <button
                      key={o.id}
                      dir="auto"
                      onClick={() => setFinalAnswers((a) => ({ ...a, [q.id]: o.id }))}
                      className={`block w-full rounded-lg border-2 px-4 py-2 text-start transition ${
                        finalAnswers[q.id] === o.id
                          ? "border-primary bg-blue-50"
                          : "border-slate-200 hover:border-primary"
                      }`}
                    >
                      {o.text}
                    </button>
                  ))}
                </div>
              ))}
              {quizResult && (
                <div
                  className={`space-y-2 rounded-lg p-4 ${
                    quizResult.passed ? "bg-emerald-50 text-success" : "bg-amber-50 text-warning"
                  }`}
                >
                  <p className="font-bold">
                    النتيجة / Score: {quizResult.score}% — {quizResult.message}
                  </p>
                  {quizResult.certificate_awarded && (
                    <p className="text-sm">
                      🎓 شهادة كفاءة مُنحت / Certificat de compétence délivré:{" "}
                      <span className="font-mono">{quizResult.certificate_awarded.serial_number}</span>
                    </p>
                  )}
                </div>
              )}
              <BilingualButton
                ar={quizResult && !quizResult.passed ? "إعادة المحاولة" : "تقديم"}
                fr={quizResult && !quizResult.passed ? "Réessayer" : "Soumettre"}
                variant="success"
                onClick={submitFinalQuiz}
              />
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
