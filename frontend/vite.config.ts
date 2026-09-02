import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Fail the build on TypeScript errors
    sourcemap: false,
    rollupOptions: {
      onwarn(warning, warn) {
        // Treat unused variable warnings as errors in production
        if (warning.code === "UNUSED_EXTERNAL_IMPORT") {
          return;
        }
        warn(warning);
      },
    },
  },
});
