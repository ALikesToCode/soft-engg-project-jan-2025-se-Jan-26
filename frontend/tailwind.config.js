/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        maroon: {
          100: '#FFE6E6',
          200: '#FFB3B3',
          300: '#FF8080',
          400: '#FF4D4D',
          500: '#FF1A1A',
          600: '#800000',
          700: '#660000',
          800: '#4D0000',
          900: '#330000',
        },
      },
    },
  },
  plugins: [],
} 