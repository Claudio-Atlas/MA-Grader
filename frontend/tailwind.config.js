/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme palette
        'dark': {
          900: '#0a0e14',  // Deepest background
          800: '#0d1117',  // Main background
          700: '#161b22',  // Card background
          600: '#21262d',  // Elevated surfaces
          500: '#30363d',  // Borders
          400: '#484f58',  // Muted elements
          300: '#6e7681',  // Muted text
          200: '#8b949e',  // Secondary text
          100: '#c9d1d9',  // Primary text
          50: '#f0f6fc',   // Bright text
        },
        'accent': {
          red: '#dc2626',
          'red-hover': '#b91c1c',
          green: '#22c55e',
          yellow: '#f59e0b',
          blue: '#3b82f6',
        }
      },
      fontFamily: {
        sans: ['Space Grotesk', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 2s linear infinite',
      }
    },
  },
  plugins: [],
}
