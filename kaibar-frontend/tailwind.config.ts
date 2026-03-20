import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "green-dark":  "#1B4332",
        "green-mid":   "#2D6A4F",
        "green-light": "#40916C",
        "gold":        "#FFD700",
        "gold-dark":   "#F59E0B",
        "yellow":      "#FDE047",
        "orange":      "#F97316",
        "orange-dark": "#EA580C",
        "kai-red":     "#E63946",
      },
      backgroundImage: {
        "gold-gradient":   "linear-gradient(135deg, #FFD700 0%, #F97316 100%)",
        "green-gradient":  "linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%)",
        "rastafari":       "linear-gradient(135deg, #E63946 0%, #FFD700 50%, #22C55E 100%)",
      },
      boxShadow: {
        "gold":   "0 0 20px rgba(255,215,0,0.35)",
        "orange": "0 0 20px rgba(249,115,22,0.35)",
        "green":  "0 0 20px rgba(64,145,108,0.35)",
      },
      animation: {
        "shimmer":    "shimmer 4s linear infinite",
        "pulse-gold": "pulse-gold 2.5s ease-in-out infinite",
        "float":      "float 3s ease-in-out infinite",
        "spin-slow":  "spin-slow 8s linear infinite",
      },
    },
  },
  plugins: [],
};
export default config;
