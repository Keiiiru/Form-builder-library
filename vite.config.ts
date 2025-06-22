import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import dts from "vite-plugin-dts"; // Для генерации .d.ts файлов

export default defineConfig({
  plugins: [
    vue(),
    dts({
      // Генерировать типы TypeScript
      insertTypesEntry: true,
    }),
  ],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
  build: {
    lib: {
      // Точка входа библиотеки
      entry: resolve(__dirname, "src/lib/vue/index.ts"),
      name: "VueFormBuilder",
      fileName: (format) => `vue-form-builder.${format}.js`,
    },
    rollupOptions: {
      // Внешние зависимости, которые не должны попадать в сборку
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: "dist", // Папка для сборки
  },
});
