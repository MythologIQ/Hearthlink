/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        starcraft: {
          blue: '#22d3ee',
          gold: '#fbbf24',
          dark: '#1e293b',
          darker: '#0f172a'
        }
      },
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
        'orbitron': ['Orbitron', 'monospace']
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'starfield': 'starfield 20s linear infinite'
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { 
            transform: 'scale(1)',
            filter: 'drop-shadow(0 0 20px rgba(34, 211, 238, 0.8))'
          },
          '50%': { 
            transform: 'scale(1.1)',
            filter: 'drop-shadow(0 0 30px rgba(34, 211, 238, 1))'
          }
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0) scale(1)' },
          '50%': { transform: 'translateY(-8px) scale(1.02)' }
        },
        'starfield': {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-100vh)' }
        }
      }
    },
  },
  plugins: [],
}