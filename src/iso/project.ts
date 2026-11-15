/**
 * Isometric projection.
 *
 * World axes: +x runs right-and-down the screen, +y runs left-and-down, +z is up.
 * The viewer looks from the +x/+y/+z side, so larger x, y or z means "closer".
 */
export type Pt = [number, number];

export interface Box {
  x: number;
  y: number;
  z: number;
  /** size along x */
  w: number;
  /** size along y */
  d: number;
  /** size along z (height) */
  h: number;
}

export const COS30 = Math.cos(Math.PI / 6);
export const SIN30 = 0.5;

export function project(x: number, y: number, z = 0): Pt {
  return [(x - y) * COS30, (x + y) * SIN30 - z];
}

const r2 = (n: number) => Math.round(n * 100) / 100;

/** SVG `points` attribute string. */
export function pts(points: Pt[]): string {
  return points.map(([a, b]) => `${r2(a)},${r2(b)}`).join(' ');
}

/** SVG path for a polyline of screen points. */
export function pathOf(points: Pt[], close = false): string {
  const d = points.map(([a, b], i) => `${i === 0 ? 'M' : 'L'}${r2(a)} ${r2(b)}`).join(' ');
  return close ? `${d} Z` : d;
}

export function boxCorners(b: Box): Pt[] {
  const out: Pt[] = [];
  for (const dx of [0, b.w]) for (const dy of [0, b.d]) for (const dz of [0, b.h]) out.push(project(b.x + dx, b.y + dy, b.z + dz));
  return out;
}

export interface Rect2 {
  x: number;
  y: number;
  w: number;
  h: number;
}

export function boundsOf(points: Pt[]): Rect2 {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const [x, y] of points) {
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

/** Screen rectangle that contains every given box, plus padding. */
export function viewRectFor(boxes: Box[], pad = 16): Rect2 {
  const b = boundsOf(boxes.flatMap(boxCorners));
  return { x: r2(b.x - pad), y: r2(b.y - pad), w: r2(b.w + pad * 2), h: r2(b.h + pad * 2) };
}

export function viewBoxAttr(r: Rect2): string {
  return `${r.x} ${r.y} ${r.w} ${r.h}`;
}

/**
 * Transforms that let you draw ordinary 2D SVG (text, rects) "printed" onto a plane.
 * In the local 2D space, +x is the reading direction and +y is "down" on the surface.
 */
/** Horizontal plane at height z. Text runs along world +x; "down" is world +y. */
export function topPlane(x: number, y: number, z: number): string {
  const [tx, ty] = project(x, y, z);
  return `matrix(${r4(COS30)} ${SIN30} ${r4(-COS30)} ${SIN30} ${r2(tx)} ${r2(ty)})`;
}
/** Vertical face that looks toward +y (the left-hand visible side). Text runs along +x; "down" is −z. */
export function leftPlane(x: number, y: number, z: number): string {
  const [tx, ty] = project(x, y, z);
  return `matrix(${r4(COS30)} ${SIN30} 0 1 ${r2(tx)} ${r2(ty)})`;
}
/** Vertical face that looks toward +x (the right-hand visible side). Text runs along −y; "down" is −z. */
export function rightPlane(x: number, y: number, z: number): string {
  const [tx, ty] = project(x, y, z);
  return `matrix(${r4(COS30)} ${-SIN30} 0 1 ${r2(tx)} ${r2(ty)})`;
}
const r4 = (n: number) => Math.round(n * 10000) / 10000;

/** An isometric circle on a horizontal plane projects to an axis-aligned ellipse with these radii. */
export function isoEllipseRadii(r: number): { rx: number; ry: number } {
  return { rx: r * Math.SQRT2 * COS30, ry: r * Math.SQRT2 * SIN30 };
}

/** Convert a screen point into percentages of a view rectangle (used to place HTML over SVG). */
export function toPercent(p: Pt, view: Rect2): { left: number; top: number } {
  return { left: ((p[0] - view.x) / view.w) * 100, top: ((p[1] - view.y) / view.h) * 100 };
}
