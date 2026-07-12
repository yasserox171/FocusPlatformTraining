import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#1B4FD8",
        success: "#059669",
        warning: "#B45309",
        danger: "#DC2626",
        surface: "#F1F5F9",
        dark: "#0F172A",
      },
      fontFamily: {
        cairo: ["Cairo", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
