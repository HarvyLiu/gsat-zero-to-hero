/** Prefix a site-absolute path with the configured base (works in Astro pages and in islands). */
export function withBase(path: string): string {
  const base = (import.meta.env?.BASE_URL ?? '/').replace(/\/$/, '');
  return `${base}${path.startsWith('/') ? path : `/${path}`}`;
}
