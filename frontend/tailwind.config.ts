import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        karma: {
          bg: '#0d0d0f',
          surface: '#16161a',
          accent: '#7f5af0',
          accent2: '#2cb67d',
          text: '#fffffe',
          muted: '#94a1b2',
          danger: '#ef4565',
          border: '#2d2040',
          'border-active': '#6d28d9',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};

export default config;
