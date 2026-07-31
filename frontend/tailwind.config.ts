import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        // CyberShield brand palette
        cyber: {
          50:  '#e6f9ff',
          100: '#b3efff',
          200: '#66dfff',
          300: '#00ccff',
          400: '#00b8e6',
          500: '#0099cc',  // Primary cyan
          600: '#007aaa',
          700: '#005c88',
          800: '#003d66',
          900: '#001f33',
        },
        dark: {
          50:  '#1a1f2e',
          100: '#151a27',
          200: '#111520',
          300: '#0d1019',
          400: '#090c12',
          500: '#05070b',  // Deepest background
        },
        threat: {
          critical: '#ff2d55',
          high:     '#ff6b35',
          medium:   '#ffd60a',
          low:      '#30d158',
          info:     '#0a84ff',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow':    'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow':          'glow 2s ease-in-out infinite alternate',
        'scan-line':     'scanLine 2s linear infinite',
        'fade-in':       'fadeIn 0.3s ease-in-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-up':   'slideInUp 0.3s ease-out',
      },
      keyframes: {
        glow: {
          '0%':   { boxShadow: '0 0 5px #00ccff, 0 0 10px #00ccff' },
          '100%': { boxShadow: '0 0 20px #00ccff, 0 0 40px #00ccff, 0 0 60px #00ccff' },
        },
        scanLine: {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInLeft: {
          '0%':   { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInUp: {
          '0%':   { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      backgroundImage: {
        'cyber-grid':    "url(\"data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300ccff' fill-opacity='0.03'%3E%3Cpath d='M0 0h40v1H0zM0 0v40h1V0z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        'gradient-cyber': 'linear-gradient(135deg, #001f33 0%, #0d1019 50%, #001a2e 100%)',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
}

export default config
