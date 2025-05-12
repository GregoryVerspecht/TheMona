import defaultTheme from 'tailwindcss/defaultTheme';
import plugin from 'tailwindcss/plugin';
import typographyPlugin from '@tailwindcss/typography';
import colors from 'tailwindcss/colors';

module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{astro,html,js,jsx,json,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    container: {
      center: true,
      padding: '2rem',
    },
    extend: {
      colors: {
        primary: 'var(--aw-color-primary)',
        secondary: 'var(--aw-color-secondary)',
        accent: 'var(--aw-color-accent)',
        default: 'var(--aw-color-text-default)',
        muted: 'var(--aw-color-text-muted)',
      },
      fontFamily: {
        sans: ['var(--aw-font-sans, ui-sans-serif)', ...defaultTheme.fontFamily.sans],
        serif: ['var(--aw-font-serif, ui-serif)', ...defaultTheme.fontFamily.serif],
        heading: ['var(--aw-font-heading, ui-sans-serif)', ...defaultTheme.fontFamily.sans],
      },

      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out forwards',
        'slide-up': 'slideUp 0.5s ease-in-out',
        'spin-slow': 'rotate 30s linear infinite',
        'gradient-move': 'gradientMove 10s ease infinite',
        'gradient-move-slow': 'gradient-move-slow 8s ease infinite',
        'gradient-move-fast': 'gradient-move-fast 4s ease-in-out infinite',
        'glow-shift': 'pulse-glow 6s ease-in-out infinite, color-shift-glow 12s ease-in-out infinite',
        fade: 'fadeInUp 1s both',

      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: 0, transform: 'translateY(2rem)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': {
            transform: 'translateY(20px)',
            opacity: '0'
          },
          '100%': {
            transform: 'translateY(0)',
            opacity: '1'
          },
        },
        gradientMove: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },

        'gradient-move-slow': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'gradient-move-fast': {
          '0%, 100%': { backgroundPosition: '100% 0%' },
          '50%': { backgroundPosition: '0% 100%' },
        },






      },

      boxShadow: {
        'xl-dark': '0 20px 25px -5px rgba(255, 255, 255, 0.1), 0 8px 10px -6px rgba(255, 255, 255, 0.1)',
      },
      backgroundImage: {
        'mona': "linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab)",
        'mona-alt': "linear-gradient(-45deg, #23d5ab, #23a6d5, #e73c7e, #ee7752)",
        'mona-glow-smooth': 'radial-gradient(ellipse at center, #0fffc1, #7e0fff, #ff00d4, #00ff94)',


      },
      

    },
    backgroundSize: {
      '200': '200% 200%',
    },
  },
  plugins: [
    typographyPlugin,
    plugin(({ addVariant }) => {
      addVariant('intersect', '&:not([no-intersect])');
    }),
  ],
};
