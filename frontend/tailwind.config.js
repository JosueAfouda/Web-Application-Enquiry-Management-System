/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        accent: {
          teal: '#14b8a6',
          deep: '#0f172a',
        },
      },
    },
  },
  plugins: [],
}
