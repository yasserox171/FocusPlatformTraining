"use client";

/** صفحة التحقق من الشهادة — عامة (بدون login) */
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface VerifyData {
  valid: boolean;
  serial_number: string;
  type: "attendance" | "competency";
  issued_at: string;
  learner_name_ar: string;
  learner_name_fr: string;
  course_title_ar: string;
  course_title_fr: string;
}

export default function VerifyPage() {
  const { serial } = useParams<{ serial: string }>();
  const [data, setData] = useState<VerifyData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`/api/verify/${serial}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setData)
      .catch(() => setError(true));
  }, [serial]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-8 shadow-md">
        <h1 className="mb-6 text-center text-xl font-bold text-primary">
          التحقق من الشهادة / Vérification du certificat
        </h1>
        {error && (
          <p className="rounded-lg bg-red-50 p-4 text-center text-danger">
            ❌ شهادة غير موجودة / Certificat introuvable
          </p>
        )}
        {data && (
          <div className="space-y-4">
            <p className="rounded-lg bg-emerald-50 p-3 text-center font-bold text-success">
              ✓ شهادة صحيحة / Certificat valide
            </p>
            <div className="rounded-lg border-4 border-double border-primary/40 bg-surface p-6 text-center">
              <p className="text-sm font-bold text-primary">Focus Platform Training</p>
              <p className="mt-3 text-lg font-bold" dir="auto">
                {data.learner_name_ar}
              </p>
              <p className="text-lg font-bold" dir="auto">
                {data.learner_name_fr}
              </p>
              <p className="mt-2 text-primary" dir="auto">
                {data.course_title_ar} / {data.course_title_fr}
              </p>
              <span
                className={`mt-3 inline-block rounded-full px-4 py-1 text-xs font-bold text-white ${
                  data.type === "competency" ? "bg-success" : "bg-primary"
                }`}
              >
                {data.type === "competency" ? "كفاءة / Compétence" : "حضورية / Présence"}
              </span>
            </div>
            <div className="text-center text-xs text-slate-500">
              <p>
                الرقم التسلسلي / N° de série: <span className="font-mono">{data.serial_number}</span>
              </p>
              <p>تاريخ الإصدار / Date: {data.issued_at}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
