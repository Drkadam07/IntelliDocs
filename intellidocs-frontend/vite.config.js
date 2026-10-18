import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxies /api/* to FastAPI (strips the /api prefix). Only used when MOCK = false in src/api.js
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": { target: "http://localhost:8000", rewrite: (p) => p.replace(/^\/api/, "") } } },
});
