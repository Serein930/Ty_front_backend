/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  safelist: [
    'bg-warning/10', 'border-warning/20', 'text-warning', 'hover:bg-warning/20',
    'bg-material/10', 'border-material/20', 'text-material', 'hover:bg-material/20',
    'bg-traffic/10', 'border-traffic/20', 'text-traffic', 'hover:bg-traffic/20',
    'bg-propaganda/10', 'border-propaganda/20', 'text-propaganda', 'hover:bg-propaganda/20',
    'border-orange-500/50', 'border-primary/50', 'border-warning/50', 'border-material/50',
    'hover:border-orange-500/50', 'hover:border-primary/50', 'hover:border-warning/50', 'hover:border-material/50',
    'bg-purple-500', 'bg-yellow-500', 'bg-blue-500'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#00f0ff', danger: '#ff3b30', warning: '#ffcc00',
        logistics: '#007aff', material: '#bd00ff', traffic: '#ff9500', propaganda: '#d946ef',
        darkBlue: '#051029', midBlue: '#0b1b38', lightBlue: '#102546',
        textGray: '#a0b1c5', panelBg: 'rgba(11, 27, 56, 0.95)', 
      },
      boxShadow: {
        'glow': '0 0 8px rgba(0, 240, 255, 0.5)',
        'glow-danger': '0 0 12px rgba(255, 59, 48, 0.6)',
        'glow-warning': '0 0 12px rgba(255, 204, 0, 0.6)',
        'glow-green': '0 0 12px rgba(34, 197, 94, 0.6)',
      },
      animation: { 
        'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite', 
        'spin-slow': 'spin 3s linear infinite'
      }
    },
  },
  plugins: [],
}