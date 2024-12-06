/** @type {import('tailwindcss').Config} */
export default {
  content: ["./layouts/**/*.html"],
  theme: {
    extend: {
      colors: {
        "brand-1": "#313866",
        "brand-2": "#504099",
        "brand-3": "#974EC3",
        "brand-4": "#FE7BE5",
      },
      fontFamily: {
        transcript: ['Courier', 'serif']
      }
    },
  },
  plugins: [],
};
