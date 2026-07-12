"use client";

/** زر ثنائي اللغة — "عربي / Français" دائماً */

const variants = {
  primary: "bg-primary text-white hover:bg-blue-700",
  success: "bg-success text-white hover:bg-emerald-700",
  danger: "bg-danger text-white hover:bg-red-700",
  outline: "border border-slate-300 text-dark hover:bg-slate-100",
} as const;

export default function BilingualButton({
  ar,
  fr,
  icon,
  variant = "primary",
  onClick,
  disabled,
  type = "button",
}: {
  ar: string;
  fr: string;
  icon?: string;
  variant?: keyof typeof variants;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-4 py-2 text-sm font-semibold transition disabled:opacity-50 ${variants[variant]}`}
    >
      {icon ? `${icon} ` : ""}
      {ar} / {fr}
    </button>
  );
}
