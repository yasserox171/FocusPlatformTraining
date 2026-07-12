"use client";

import { getAccessToken } from "@/lib/api";
import type { Certificate } from "@/lib/types";

const TYPE_LABELS = {
  attendance: "حضورية / Présence",
  competency: "كفاءة / Compétence",
} as const;

export default function CertificateCard({ cert }: { cert: Certificate }) {
  const download = async () => {
    const res = await fetch(`/api/learner/certificates/${cert.id}/download`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${cert.serial_number}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 dir="auto" className="font-bold">
            {cert.course.title_ar}
          </h3>
          <p dir="auto" className="text-sm text-slate-500">
            {cert.course.title_fr}
          </p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-bold text-white ${
            cert.type === "competency" ? "bg-success" : "bg-primary"
          }`}
        >
          {TYPE_LABELS[cert.type]}
        </span>
      </div>
      <div className="rounded-lg border-4 border-double border-primary/40 bg-surface p-6 text-center">
        <p className="text-sm font-bold text-primary">Focus Platform Training</p>
        <p className="mt-1 text-xs text-slate-500">شهادة / Certificat</p>
      </div>
      <p className="text-xs text-slate-500">
        الرقم التسلسلي / N° de série: <span className="font-mono">{cert.serial_number}</span>
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={download}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        >
          📄 تنزيل PDF / Télécharger
        </button>
        <a
          href={cert.linkedin_url}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold hover:bg-slate-100"
        >
          💼 LinkedIn
        </a>
      </div>
    </div>
  );
}
