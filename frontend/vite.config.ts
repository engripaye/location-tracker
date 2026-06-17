import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://127.0.0.1:8000",
      "/sessions": "http://127.0.0.1:8000",
      "/track": "http://127.0.0.1:8000",
      "/sos": "http://127.0.0.1:8000"
    }
  }
});
