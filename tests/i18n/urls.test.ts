/**
 * Locale-aware URLs (src/i18n/urls.ts on src/lib/paths.ts) with the real base '/' and with an
 * emulated GitHub Pages base '/repo/' (vi.stubEnv sets import.meta.env.BASE_URL, which both helpers
 * read at call time). Every site URL ends with '/' (astro.config trailingSlash: 'always').
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { alternatePath, localeOf, localizedPath, stripBase } from '../../src/i18n/urls';
import { withBase } from '../../src/lib/paths';

const PAGES = ['/zh-tw/', '/zh-tw/math/', '/zh-tw/math/real-numbers/', '/zh-tw/site/welcome/', '/zh-tw/math/glossary/'];

describe('with base "/"', () => {
  it('builds localized paths with one trailing slash', () => {
    expect(localizedPath('zh-tw')).toBe('/zh-tw/');
    expect(localizedPath('en', 'math')).toBe('/en/math/');
    expect(localizedPath('zh-tw', 'math', 'real-numbers')).toBe('/zh-tw/math/real-numbers/');
    expect(localizedPath('en', '', 'math', '')).toBe('/en/math/');
  });

  it('reads the locale from a pathname', () => {
    expect(localeOf('/zh-tw/math/real-numbers/')).toBe('zh-tw');
    expect(localeOf('/en/')).toBe('en');
    expect(localeOf('/en')).toBe('en');
    expect(localeOf('/')).toBeUndefined();
    expect(localeOf('/english/')).toBeUndefined();
    expect(localeOf('/zh-tw-extra/')).toBeUndefined();
  });

  it('maps a page to the same page in the other locale, and back', () => {
    expect(alternatePath('/zh-tw/math/real-numbers/', 'en')).toBe('/en/math/real-numbers/');
    expect(alternatePath('/en/math/real-numbers', 'zh-tw')).toBe('/zh-tw/math/real-numbers/');
    expect(alternatePath('/en/', 'en')).toBe('/en/');
    for (const p of PAGES) expect(alternatePath(alternatePath(p, 'en'), 'zh-tw')).toBe(p);
  });

  it('sends non-localized pages (the root chooser, 404) to the target home', () => {
    expect(alternatePath('/', 'en')).toBe('/en/');
    expect(alternatePath('/404/', 'zh-tw')).toBe('/zh-tw/');
  });

  it('leaves paths alone in stripBase and withBase', () => {
    expect(stripBase('/zh-tw/')).toBe('/zh-tw/');
    expect(withBase('/x/')).toBe('/x/');
    expect(withBase('x/')).toBe('/x/');
  });
});

describe('with an emulated base "/repo/"', () => {
  afterEach(() => vi.unstubAllEnvs());
  const repo = () => vi.stubEnv('BASE_URL', '/repo/');

  it('prefixes every built path with the base', () => {
    repo();
    expect(withBase('/characters/teacher.svg')).toBe('/repo/characters/teacher.svg');
    expect(localizedPath('zh-tw')).toBe('/repo/zh-tw/');
    expect(localizedPath('en', 'math', 'real-numbers')).toBe('/repo/en/math/real-numbers/');
  });

  it('strips the base before reading the locale', () => {
    repo();
    expect(stripBase('/repo/zh-tw/math/')).toBe('/zh-tw/math/');
    expect(stripBase('/repo')).toBe('/');
    expect(localeOf('/repo/en/math/')).toBe('en');
    expect(localeOf('/repo/')).toBeUndefined();
  });

  it('keeps the base when switching locale', () => {
    repo();
    expect(alternatePath('/repo/zh-tw/math/real-numbers/', 'en')).toBe('/repo/en/math/real-numbers/');
    expect(alternatePath('/repo/', 'en')).toBe('/repo/en/');
    for (const p of PAGES.map((x) => `/repo${x}`)) expect(alternatePath(alternatePath(p, 'en'), 'zh-tw')).toBe(p);
  });

  it('a base without a trailing slash behaves the same', () => {
    vi.stubEnv('BASE_URL', '/repo');
    expect(localizedPath('en', 'math')).toBe('/repo/en/math/');
    expect(alternatePath('/repo/en/math/', 'zh-tw')).toBe('/repo/zh-tw/math/');
  });
});
