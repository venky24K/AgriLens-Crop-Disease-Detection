/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        pastelGreen: '#E6F4EA',
        softLavender: '#EAE6F8',
        lightTeal: '#DFF5F2',
        accentGradientStart: '#4ADE80', // Green
        accentGradientEnd: '#3B82F6',   // Blue
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
