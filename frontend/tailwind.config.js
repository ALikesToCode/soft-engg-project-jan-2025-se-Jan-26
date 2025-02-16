import forms from '@tailwindcss/forms'

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
          50: '#fdf2f2',
          100: '#f3e2e2',
          200: '#dbc1c1',
          300: '#c39e9e',
          400: '#a67979',
          500: '#8b4444',
          600: '#722b2b',
          700: '#591f1f',
          800: '#411616',
          900: '#2c0f0f',
        },
        yellow: {
          50: '#fdfaeb',
          100: '#fdf2c7',
          200: '#f8e3a3',
          300: '#f6d47e',
          400: '#e9b64d',
          500: '#d49b35',
          600: '#b37d24',
          700: '#8c5e1a',
          800: '#674415',
          900: '#4d3110',
        },
      },
    },
  },
  plugins: [forms],
} 