/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js",
    "./app/static/**/*.css"
  ],
  theme: {
    extend: {},
    screens: {
      'sm': '640px',
      'md': 'min-width: 750px', // Custom breakpoint for min-width:750px
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    }
  },
  plugins: [],
}
