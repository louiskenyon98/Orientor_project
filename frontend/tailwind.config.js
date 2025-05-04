/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors
        primary: {
          blue: '#3B82F6',
          indigo: '#6366F1',
          teal: '#59C2C9',
          purple: '#7D5BA6',
          lilac: '#A78BDA',
        },
        // Accent colors
        accent: {
          teal: '#38B2AC',
          amber: '#F59E0B',
        },
        // Neutral palette
        neutral: {
          50: '#F7F9FC',
          100: '#EDF2F7',
          200: '#E2E8F0',
          300: '#CBD5E0',
          400: '#A0AEC0',
          500: '#718096',
          600: '#4A5568',
          700: '#2D3748',
          800: '#1A202C',
          900: '#171923',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(#f7f9fc, #ffffff)',
        'branch-pattern': "url('/patterns/branch.svg')",
        'grid-pattern': "url('/patterns/grid.svg')",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(0,0,0,0.05)',
        'glass': '0 4px 30px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'float': 'float 6s ease-in-out infinite',
        'grow': 'grow 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        grow: {
          '0%': { transform: 'scaleX(0)' },
          '100%': { transform: 'scaleX(1)' },
        },
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#333',
            a: {
              color: '#3B82F6',
              '&:hover': {
                color: '#2563EB',
              },
            },
            h1: {
              fontFamily: 'Playfair Display',
              fontWeight: '300',
              letterSpacing: '0.05em',
            },
            h2: {
              fontFamily: 'Playfair Display',
              fontWeight: '300',
              letterSpacing: '0.05em',
            },
            h3: {
              fontFamily: 'Playfair Display',
              fontWeight: '300',
              letterSpacing: '0.05em',
            },
          },
        },
        dark: {
          css: {
            color: '#e2e8f0',
            a: {
              color: '#60a5fa',
              '&:hover': {
                color: '#93c5fd',
              },
            },
            h1: {
              color: '#f7fafc',
            },
            h2: {
              color: '#f7fafc',
            },
            h3: {
              color: '#f7fafc',
            },
            strong: {
              color: '#f7fafc',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};