"use client";

import { useCallback, useEffect, useState } from "react";
import BilingualButton from "@/components/bilingual/BilingualButton";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";

const input = "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    email: "",
    password: "",
    role: "learner" as "admin" | "learner",
    full_name_ar: "",
    full_name_fr: "",
  });

  const load = useCallback(() => {
    api<User[]>("/api/admin/users").then(setUsers).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api("/api/admin/users", { method: "POST", body: JSON.stringify(form) });
      setForm({ email: "", password: "", role: "learner", full_name_ar: "", full_name_fr: "" });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "خطأ / Erreur");
    }
  };

  const toggleActive = async (u: User) => {
    await api(`/api/admin/users/${u.id}`, {
      method: "PUT",
      body: JSON.stringify({ is_active: !u.is_active }),
    });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">المستخدمون / Utilisateurs</h1>

      <form onSubmit={create} className="grid gap-3 rounded-xl bg-white p-6 shadow-sm sm:grid-cols-2 lg:grid-cols-3">
        <input dir="ltr" type="email" required className={input} placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input dir="ltr" type="password" required className={input} placeholder="Mot de passe / كلمة المرور" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <select className={input} value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as "admin" | "learner" })}>
          <option value="learner">متعلم / Apprenant</option>
          <option value="admin">أدمين / Admin</option>
        </select>
        <input dir="rtl" required className={input} placeholder="الاسم الكامل بالعربية" value={form.full_name_ar} onChange={(e) => setForm({ ...form, full_name_ar: e.target.value })} />
        <input dir="ltr" required className={input} placeholder="Nom complet en français" value={form.full_name_fr} onChange={(e) => setForm({ ...form, full_name_fr: e.target.value })} />
        <BilingualButton ar="إنشاء حساب" fr="Créer" type="submit" />
      </form>

      {error && <p className="rounded-lg bg-red-50 p-4 text-danger">{error}</p>}

      <div className="overflow-x-auto rounded-xl bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-surface text-start">
            <tr>
              <th className="p-3 text-start">الاسم / Nom</th>
              <th className="p-3 text-start">Email</th>
              <th className="p-3 text-start">الدور / Rôle</th>
              <th className="p-3 text-start">الحالة / Statut</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-slate-100">
                <td dir="auto" className="p-3">
                  {u.full_name_ar} / {u.full_name_fr}
                </td>
                <td dir="ltr" className="p-3 text-start">
                  {u.email}
                </td>
                <td className="p-3">{u.role === "admin" ? "أدمين / Admin" : "متعلم / Apprenant"}</td>
                <td className="p-3">
                  <span className={`rounded px-2 py-0.5 text-xs font-semibold ${u.is_active ? "bg-emerald-100 text-success" : "bg-red-100 text-danger"}`}>
                    {u.is_active ? "مفعّل / Actif" : "معطّل / Désactivé"}
                  </span>
                </td>
                <td className="p-3">
                  <button onClick={() => toggleActive(u)} className="text-sm text-primary hover:underline">
                    {u.is_active ? "تعطيل / Désactiver" : "تفعيل / Activer"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
