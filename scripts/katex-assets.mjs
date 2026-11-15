/**
 * Self-hosts KaTeX's stylesheet and fonts (MIT). Keeps only woff2 so the CSS never asks for woff/ttf.
 * Run: node scripts/katex-assets.mjs   (also part of `npm run assets`)
 */
import { copyFileSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'node_modules', 'katex', 'dist');
const out = join(root, 'public', 'katex');
mkdirSync(join(out, 'fonts'), { recursive: true });
let n = 0;
for (const f of readdirSync(join(dist, 'fonts'))) if (f.endsWith('.woff2')) { copyFileSync(join(dist, 'fonts', f), join(out, 'fonts', f)); n++; }
const css = readFileSync(join(dist, 'katex.min.css'), 'utf8')
  .replace(/,url\(fonts\/[^)]+\.woff\) format\("woff"\)/g, '')
  .replace(/,url\(fonts\/[^)]+\.ttf\) format\("truetype"\)/g, '');
if (/\.woff\)|\.ttf\)/.test(css)) throw new Error('KaTeX CSS still references woff/ttf; check its format');
writeFileSync(join(out, 'katex.min.css'), css);
const version = JSON.parse(readFileSync(join(root, 'node_modules', 'katex', 'package.json'), 'utf8')).version;
console.log(`katex ${version}: ${n} woff2 fonts + katex.min.css → public/katex`);
