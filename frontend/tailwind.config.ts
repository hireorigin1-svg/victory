import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        panel: "#f7f7f2",
        signal: "#1e7f6f",
        caution: "#b25e09",
        line: "#d8d8cf"
      }
    }
  },
  plugins: []
};

export default config;
