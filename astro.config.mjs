import { defineConfig } from 'astro/config';

// GitHub Pages 项目站部署在子路径 /ai-org-site/ 下，需配 base。
// 若日后用自定义域名，把 base 改回 '/'。
export default defineConfig({
  site: 'https://zhao1bo-source.github.io',
  base: '/ai-org-site/',
});
