/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "selector",
  content: ["./layouts/**/*.html"],
  theme: {
    screens: {
      sm: "48rem", // 768px (at font size 16)

      md: "64rem", // 1024px

      lg: "85.375rem", // 1366px

      xl: "120rem", // 1920px

      "2xl": "160rem", // 2560px
    },
    extend: {},
  },
  plugins: [],
};
