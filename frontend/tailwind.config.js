/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'gray-900': '#0d1117',
        'gray-800': '#161b22',
        'gray-700': '#21262d',
        'cyan-accent': '#00A8E8',
        'cyan-hover': '#007EA7',

        // AJOUTEZ CES COULEURS
        'light-bg': '#ffffff',      // Fond clair (blanc)
        'light-text': '#0d1117',    // Texte clair (votre gris le plus foncé)
        'dark-bg': '#0d1117',       // Fond sombre (votre gris le plus foncé)
        'dark-text': '#f0f6fc',     // Texte sombre (un blanc cassé)
      },
    },
  },
  plugins: [],
}