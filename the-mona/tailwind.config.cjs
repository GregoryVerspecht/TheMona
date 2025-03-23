const colors = require('tailwindcss/colors');

module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,vue}'],
  theme: {
    container: {
      center: true,
      padding: '2rem',
    },
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out forwards',
        'slide-up': 'slideUp 0.5s ease-in-out',
        'spin-slow': 'rotate 30s linear infinite',
        'gradient-move': 'gradientMove 10s ease infinite',
      },
      keyframes: {
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

      },
      colors: {
        primary: '#FF6F61',
        secondary: '#6B5B95',
        darkbg: '#1A1A1A',
        lightbg: '#F4F4F4',
        slate: colors.slate, 
      },
      boxShadow: {
        'xl-dark': '0 20px 25px -5px rgba(255, 255, 255, 0.1), 0 8px 10px -6px rgba(255, 255, 255, 0.1)',
      },
      backgroundImage: {
        'mona': "linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab)",
        'mona-alt': "linear-gradient(-45deg, #23d5ab, #23a6d5, #e73c7e, #ee7752)",
      },
    },
    backgroundSize: {
      '200': '200% 200%',
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms')({ strategy: 'class' }),
  ],
};

