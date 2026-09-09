import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#070b13",
        surface: "#0c121e",
        "surface-raised": "#121b2c",
        "surface-hover": "#1a263e",
        border: "#1f2e4a",
        "border-subtle": "#162238",
        
        nexus: {
          50: "#f0f7ff",
          100: "#e0effe",
          200: "#bae0fd",
          300: "#7cc5fb",
          400: "#38a5f6",
          500: "#0e87ea",
          600: "#0269c7",
          700: "#0354a1",
          800: "#074785",
          900: "#0c3b6e",
          950: "#072448",
        },
        
        // Security / Risk palette
        risk: {
          low: "#10b981",
          moderate: "#f59e0b",
          high: "#f97316",
          critical: "#ef4444",
        }
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Liberation Mono", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px -5px rgba(14, 135, 234, 0.3)",
        "glow-red": "0 0 20px -5px rgba(239, 68, 68, 0.3)",
      }
    },
  },
  plugins: [],
};

export default config;
