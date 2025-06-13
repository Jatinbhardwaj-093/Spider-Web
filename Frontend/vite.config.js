import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: "dist",
    sourcemap: false,
    minify: "terser",
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/api": {
        target:
          process.env.NODE_ENV === "production"
            ? "https://your-vercel-app.vercel.app"
            : "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/health": {
        target:
          process.env.NODE_ENV === "production"
            ? "https://your-vercel-app.vercel.app"
            : "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
