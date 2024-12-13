/** @type {import('tailwindcss').Config} */
export default {
  content: ["./layouts/**/*.html"],
  theme: {
    screens: {
      sm: "48rem", // 768px (at font size 16)

      md: "64rem", // 1024px

      lg: "85.375rem", // 1366px

      xl: "120rem", // 1920px

      "2xl": "160rem", // 2560px
    },
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
