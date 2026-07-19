/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: '#2563EB',
        secondary: '#3B82F6',
        accent: '#F97316',
        background: '#F8FAFC',
        foreground: '#1E293B',
      },
    },
  },
  plugins: [],
}
