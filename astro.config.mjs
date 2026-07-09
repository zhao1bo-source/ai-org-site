import { defineConfig } from 'astro/config';

// base 通过环境变量切换：
//   GitHub Pages 项目站 → /ai-org-site/
//   Cloudflare Pages / 自定义域名 → /
const base = process.env.ASTRO_BASE || '/';

export default defineConfig({
  site: 'https://zhao1bo-source.github.io',
  base,
});
