// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkDialogue from './src/plugins/remark-dialogue.ts';
import remarkTermFirst from './src/plugins/remark-term-first.ts';

const base = '/';

export default defineConfig({
  // hreflang and the sitemap need absolute URLs. The real domain is an owner decision (docs/plan.md).
  site: process.env.SITE_URL ?? 'https://gsat-zero-to-hero.pages.dev',
  base,
  trailingSlash: 'always',
  build: { format: 'directory' },
  i18n: {
    locales: ['zh-tw', 'en'],
    defaultLocale: 'zh-tw',
    routing: { prefixDefaultLocale: true, redirectToDefaultLocale: false },
  },
  integrations: [
    react(),
    mdx(),
    sitemap({ i18n: { defaultLocale: 'zh-tw', locales: { 'zh-tw': 'zh-TW', en: 'en' } } }),
  ],
  markdown: {
    // The explicit unified() processor keeps remark plugins running (as in the ASMC reference).
    processor: unified({
      remarkPlugins: [remarkMath, [remarkDialogue, { base }], remarkTermFirst],
      rehypePlugins: [[rehypeKatex, { strict: 'warn' }]],
    }),
    shikiConfig: { theme: 'catppuccin-mocha' },
  },
});
