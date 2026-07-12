"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { api, getAccessToken } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    if (!getAccessToken()) {
      router.replace("/login");
      return;
    }
    api<{ role: string }>("/api/auth/me")
      .then((me) => router.replace(me.role === "admin" ? "/admin/dashboard" : "/dashboard"))
      .catch(() => router.replace("/login"));
  }, [router]);
  return <div className="flex min-h-screen items-center justify-center text-slate-500">جارٍ التحميل / Chargement...</div>;
}
