/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0E1116",
        panel: "#141920",
        "panel-raised": "#181F28",
        hairline: "#262E3A",
        ink: "#ECEEF1",
        "ink-muted": "#8B93A3",
        "ink-faint": "#5A6472",
        scan: "#6FE3FF",
        signal: "#FFB238",
        gap: "#E2725B",
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-plex-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "ui-monospace", "monospace"],
      },
      maxWidth: {
        prose: "68ch",
      },
    },
  },
  plugins: [],
};
