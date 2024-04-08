module.exports = {
  purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        'purple-900': '#5B21B6', // Replace with your exact purple color
        'purple-700': '#6D28D9', // Replace with your exact purple color
      },
      boxShadow: {
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)', // Adjust shadow as needed
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
