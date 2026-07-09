#!/usr/bin/env bash
# 部署到 Cloudflare Pages（直接上传 dist/，不经构建 runner）
#
# 首次使用：
#   1. npx wrangler login   # 浏览器授权 Cloudflare
#   2. bash scripts/deploy-cloudflare.sh
#
# 产出：https://ai-org-site.pages.dev （首次部署自动创建项目）

set -e
cd "$(dirname "$0")/.."

# Cloudflare 用根路径，GitHub Pages 用子路径
export ASTRO_BASE=/

echo "=== 构建（根路径）==="
npm run build

echo "=== 部署到 Cloudflare Pages ==="
# --project-name 首次会自动创建；--branch main 设为生产分支
npx wrangler pages deploy dist --project-name=ai-org-site --branch=main
