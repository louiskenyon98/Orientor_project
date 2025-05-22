/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Stitch Design Theme Colors
        stitch: {
          primary: '#e6f5e6', // mint forest green (primary background)
          accent: '#19b219', // deep green for progress, highlights
          sage: '#6b9a6b', // sage green for secondary info
          border: '#254625', // subtle separator
          track: '#366336', // progress track
        },
        // Primary colors
        primary: {
          blue: '#3B82F6',
          indigo: '#6366F1',
          teal: '#59C2C9',
          purple: '#7D5BA6',
          lilac: '#A78BDA',
          green: '#19b219', // Updated to match accent green
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
          800: '#1A1A1A', // Couleur de texte principale
          900: '#171923',
        },
        // Thème clair et sombre
        light: {
          background: '#e6f5e6', // Mint color for light mode
          text: '#2c4c2c', // Darker text for better contrast on light background
          cta: '#19b219', // Keeping the accent green
        },
        dark: {
          background: '#0a140a', // Darker version of mint forest green
          text: '#95c695', // Sage text
          cta: '#19b219', // Accent green
        },
        // Domain-based theming
        domain: {
          builder: '#F97316', // Orange for Builder domain
          communicator: '#3B82F6', // Blue for Communicator domain
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(#f7f9fc, #ffffff)',
        'branch-pattern': "url('/patterns/branch.svg')",
        'grid-pattern': "url('/patterns/grid.svg')",
        'stitch-pattern': "linear-gradient(rgba(25, 178, 25, 0.05), rgba(25, 178, 25, 0.05)), url('/patterns/branch.svg')",
      },
      fontFamily: {
        sans: ['Noto Sans', 'system-ui', 'sans-serif'],
        mono: ['inter', 'monospace'],
        departure: ['inter', 'monospace'],
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(0,0,0,0.05)',
        'glass': '0 4px 30px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'float': 'float 6s ease-in-out infinite',
        'grow': 'grow 0.3s ease-out',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
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
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.85' },
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
    container: {
      center: true,
      padding: '2.5rem', // px-40 as specified
      screens: {
        DEFAULT: '960px', // max-w-960px as specified
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/container-queries'),
  ],
};