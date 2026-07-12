/** badge يمين الكتلة: AR أو FR */
export default function LangBadge({ lang }: { lang: "ar" | "fr" | "auto" }) {
  if (lang === "auto") return null;
  return (
    <span className="absolute left-3 top-3 rounded bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-500">
      {lang.toUpperCase()}
    </span>
  );
}
