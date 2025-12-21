/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'linde-red': '#C8102E',
                'soft-red': '#fee2e2', // Still useful for user message backgrounds
                'soft-red-border': '#fecaca',
                'soft-grey': '#f3f4f6',
                'soft-grey-dark': '#e5e7eb',
            },
        },
    },
    plugins: [],
}
