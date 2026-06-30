// vite.config.js
import { defineConfig } from "file:///C:/Users/sriva/CascadeProjects/memento-ai/frontend/node_modules/vite/dist/node/index.js";
import react from "file:///C:/Users/sriva/CascadeProjects/memento-ai/frontend/node_modules/@vitejs/plugin-react/dist/index.js";
var vite_config_default = defineConfig({
  plugins: [react()],
  resolve: {
    dedupe: ["react", "react-dom"]
  },
  server: {
    port: 5174,
    headers: {
      "Cache-Control": "no-store"
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  },
  build: {
    // Ensure service worker is copied to dist
    assetsInclude: ["**/*.json", "**/*.js"]
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxzcml2YVxcXFxDYXNjYWRlUHJvamVjdHNcXFxcbWVtZW50by1haVxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiQzpcXFxcVXNlcnNcXFxcc3JpdmFcXFxcQ2FzY2FkZVByb2plY3RzXFxcXG1lbWVudG8tYWlcXFxcZnJvbnRlbmRcXFxcdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0M6L1VzZXJzL3NyaXZhL0Nhc2NhZGVQcm9qZWN0cy9tZW1lbnRvLWFpL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcclxuaW1wb3J0IHJlYWN0IGZyb20gJ0B2aXRlanMvcGx1Z2luLXJlYWN0J1xyXG5cclxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcclxuICBwbHVnaW5zOiBbcmVhY3QoKV0sXHJcbiAgcmVzb2x2ZToge1xyXG4gICAgZGVkdXBlOiBbJ3JlYWN0JywgJ3JlYWN0LWRvbSddXHJcbiAgfSxcclxuICBzZXJ2ZXI6IHtcclxuICAgIHBvcnQ6IDUxNzQsXHJcbiAgICBoZWFkZXJzOiB7XHJcbiAgICAgICdDYWNoZS1Db250cm9sJzogJ25vLXN0b3JlJ1xyXG4gICAgfSxcclxuICAgIHByb3h5OiB7XHJcbiAgICAgICcvYXBpJzoge1xyXG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly8xMjcuMC4wLjE6ODAwMCcsXHJcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxyXG4gICAgICAgIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC9hcGkvLCAnJylcclxuICAgICAgfVxyXG4gICAgfVxyXG4gIH0sXHJcbiAgYnVpbGQ6IHtcclxuICAgIC8vIEVuc3VyZSBzZXJ2aWNlIHdvcmtlciBpcyBjb3BpZWQgdG8gZGlzdFxyXG4gICAgYXNzZXRzSW5jbHVkZTogWycqKi8qLmpzb24nLCAnKiovKi5qcyddXHJcbiAgfVxyXG59KVxyXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQW9WLFNBQVMsb0JBQW9CO0FBQ2pYLE9BQU8sV0FBVztBQUVsQixJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsTUFBTSxDQUFDO0FBQUEsRUFDakIsU0FBUztBQUFBLElBQ1AsUUFBUSxDQUFDLFNBQVMsV0FBVztBQUFBLEVBQy9CO0FBQUEsRUFDQSxRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixTQUFTO0FBQUEsTUFDUCxpQkFBaUI7QUFBQSxJQUNuQjtBQUFBLElBQ0EsT0FBTztBQUFBLE1BQ0wsUUFBUTtBQUFBLFFBQ04sUUFBUTtBQUFBLFFBQ1IsY0FBYztBQUFBLFFBQ2QsU0FBUyxDQUFDLFNBQVMsS0FBSyxRQUFRLFVBQVUsRUFBRTtBQUFBLE1BQzlDO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLE9BQU87QUFBQTtBQUFBLElBRUwsZUFBZSxDQUFDLGFBQWEsU0FBUztBQUFBLEVBQ3hDO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
