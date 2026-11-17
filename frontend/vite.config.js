import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server runs on port 5173 and forwards /api calls to the back end.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
