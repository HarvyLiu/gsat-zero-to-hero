/**
 * Locale-aware URLs. Every link goes through these helpers (built on withBase), so changing the
 * deploy base is a one-line config change. Our own helper avoids depending on whether Astro's
 * getRelativeLocaleUrl prepends `base` (unverified, docs/design/05-platform.md §2).
 */
import type { Locale } from '../data/characters.ts';
import { withBase } from '../lib/paths.ts';

const LOCALE_RE = /^\/(zh-tw|en)(?=\/|$)/;

/** '/zh-tw/math/real-numbers/' for (zh-tw, 'math', 'real-numbers'); always a trailing slash. */
export function localizedPath(locale: Locale, ...segments: string[]): string {
  const rest = segments.filter(Boolean).join('/');
  return withBase(`/${locale}/${rest ? `${rest}/` : ''}`);
}

/** Strip the deploy base from a pathname. */
export function stripBase(pathname: string): string {
  const base = (import.meta.env?.BASE_URL ?? '/').replace(/\/$/, '');
  return base && (pathname === base || pathname.startsWith(`${base}/`)) ? pathname.slice(base.length) || '/' : pathname;
}

/** The locale encoded in a pathname, if any. */
export function localeOf(pathname: string): Locale | undefined {
  const m = LOCALE_RE.exec(stripBase(pathname));
  return m ? (m[1] as Locale) : undefined;
}

/** The same page in another locale: '/zh-tw/math/x/' → '/en/math/x/'. Non-localized paths go to the target's home. */
export function alternatePath(pathname: string, target: Locale): string {
  const path = stripBase(pathname);
  if (!LOCALE_RE.test(path)) return localizedPath(target);
  const swapped = path.replace(LOCALE_RE, `/${target}`);
  return withBase(swapped.endsWith('/') ? swapped : `${swapped}/`);
}
