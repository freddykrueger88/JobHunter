/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Girls Mode 🌸
        girls: {
          primary: '#ff6eb4',
          secondary: '#ffb3d9',
          bg: '#fff0f7',
          surface: '#ffe4f2',
          text: '#7a1a4b',
        },
        // Boys Mode
        boys: {
          primary: '#1e6fdb',
          secondary: '#3a8ef6',
          bg: '#0d1117',
          surface: '#161b22',
          text: '#c9d1d9',
        },
      },
    },
  },
  plugins: [],
}
