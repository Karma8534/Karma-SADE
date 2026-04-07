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
        // Karma dark theme palette
        karma: {
          bg:       "#0d0d0f",
          surface:  "#16161a",
          border:   "#2a2a35",
          accent:   "#7f5af0",
          accent2:  "#2cb67d",
          text:     "#fffffe",
          muted:    "#94a1b2",
          danger:   "#ef4565",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
