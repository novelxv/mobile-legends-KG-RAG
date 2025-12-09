/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'ml-primary': '#1a2332',     // Deep navy
        'ml-secondary': '#2a3f5f',   // Medium navy
        'ml-accent': '#f4c430',      // Bright gold
        'ml-blue': '#4da6ff',        // Bright blue
        'ml-cyan': '#00d9ff',        // Cyan glow
        'ml-dark': '#0a0e1a',        // Very dark bg
        'ml-darker': '#05070f',      // Darkest
        'ml-light': '#e8eef5',       // Light text
        'ml-purple': '#a855f7',      // Purple magic
        'ml-red': '#ef4444',         // Red danger
        'ml-green': '#10b981',       // Green success
        'ml-orange': '#f97316',      // Orange warning
      },
      fontFamily: {
        'ml': ['"Segoe UI"', 'Arial', 'sans-serif'],
        'heading': ['"Arial Black"', 'Arial', 'sans-serif'],
      },
      backgroundImage: {
        'ml-gradient': 'linear-gradient(135deg, #1a2332 0%, #2a3f5f 50%, #1a2332 100%)',
        'ml-dark-gradient': 'linear-gradient(180deg, #0a0e1a 0%, #1a2332 100%)',
        'ml-shine': 'linear-gradient(90deg, transparent, rgba(244, 196, 48, 0.3), transparent)',
        'hero-pattern': 'radial-gradient(circle at 50% 50%, rgba(77, 166, 255, 0.1) 0%, transparent 70%)',
      },
      boxShadow: {
        'ml': '0 0 30px rgba(244, 196, 48, 0.4)',
        'ml-hover': '0 0 40px rgba(244, 196, 48, 0.6)',
        'ml-glow': '0 0 20px rgba(77, 166, 255, 0.5)',
        'ml-inner': 'inset 0 0 20px rgba(244, 196, 48, 0.2)',
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(244, 196, 48, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(244, 196, 48, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      }
    },
  },
  plugins: [],
}
