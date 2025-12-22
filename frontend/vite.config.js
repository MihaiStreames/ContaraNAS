import { defineConfig } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";
import webfontDownload from "vite-plugin-webfont-dl";

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

// https://vite.dev/config/
// @ts-nocheck
export default defineConfig({
  plugins: [
    sveltekit(),

    // Download and self-host Google Fonts
    webfontDownload([
      "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ]),
  ],

  build: {
    target: "esnext",
    minify: "esbuild",
    sourcemap: false,
  },

  // Pre-bundle Tauri dependencies
  optimizeDeps: {
    include: ["@tauri-apps/api", "@tauri-apps/plugin-opener"],
  },

  // Tauri-specific configuration
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1421,
        }
      : undefined,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
});
