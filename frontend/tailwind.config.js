/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
      colors: {
        ink: { 950:'#070910', 900:'#0b0e14', 850:'#10141d', 800:'#151a24', 700:'#1d2430', 600:'#283041', 500:'#3a4456' },
        line: '#222a38',
        mut: '#8a94a6',
        acc: { personal: '#34d399', work: '#f59e0b' },
      },
      boxShadow: { tile: '0 1px 0 rgba(255,255,255,0.03) inset, 0 8px 24px rgba(0,0,0,0.35)' },
    },
  },
  plugins: [],
}
