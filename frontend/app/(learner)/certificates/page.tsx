"use client";

import { useEffect, useState } from "react";
import CertificateCard from "@/components/certificate/CertificateCard";
import { api } from "@/lib/api";
import type { Certificate } from "@/lib/types";

export default function CertificatesPage() {
  const [certs, setCerts] = useState<Certificate[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Certificate[]>("/api/learner/certificates").then(setCerts).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>;
  if (!certs) return <p className="text-slate-500">جارٍ التحميل / Chargement...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">شهاداتي / Mes certificats</h1>
      {certs.length === 0 ? (
        <p className="rounded-xl bg-white p-8 text-center text-slate-500 shadow-sm">
          لا شهادات بعد — أكمل دورة للحصول على شهادتك الأولى!
          <br />
          Pas encore de certificats — complétez une formation !
        </p>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {certs.map((c) => (
            <CertificateCard key={c.id} cert={c} />
          ))}
        </div>
      )}
    </div>
  );
}
