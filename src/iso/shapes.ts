import { type Box, type Pt, project, isoEllipseRadii } from './project';
import { luminance, shade } from './palette';

export type FaceSide = 'top' | 'left' | 'right';

export interface Face {
  side: FaceSide;
  points: Pt[];
  fill: string;
}

export interface BoxColors {
  /** color of the top face; defaults to the base color */
  top?: string;
  /** color of the left (+y) face; defaults to base darkened 15% */
  left?: string;
  /** color of the right (+x) face; defaults to base darkened 30% */
  right?: string;
}

/** Near-black colors can't get darker, so their sides keep the base and their top gets lighter instead. */
const isDark = (color: string) => luminance(color) < 0.05;

/** The default top/left/right fills for a part of this color. Light comes from the upper left, as in the reference. */
export function faceColors(color: string, colors: BoxColors = {}): Required<BoxColors> {
  const dark = isDark(color);
  return {
    top: colors.top ?? (dark ? shade(color, 0.1) : color),
    left: colors.left ?? (dark ? color : shade(color, -0.15)),
    right: colors.right ?? shade(color, -0.3),
  };
}

/** The three visible faces of an axis-aligned box, in a safe draw order (sides first, top last). */
export function boxFaces(b: Box, color: string, colors: BoxColors = {}): Face[] {
  const { x, y, z, w, d, h } = b;
  const c = faceColors(color, colors);
  const top: Pt[] = [project(x, y, z + h), project(x + w, y, z + h), project(x + w, y + d, z + h), project(x, y + d, z + h)];
  const left: Pt[] = [project(x, y + d, z), project(x + w, y + d, z), project(x + w, y + d, z + h), project(x, y + d, z + h)];
  const right: Pt[] = [project(x + w, y, z), project(x + w, y + d, z), project(x + w, y + d, z + h), project(x + w, y, z + h)];
  return [
    { side: 'left', points: left, fill: c.left },
    { side: 'right', points: right, fill: c.right },
    { side: 'top', points: top, fill: c.top },
  ];
}

/**
 * A box with rounded vertical corners (a board or slab), as polygons.
 * Corner arcs are sampled in `steps` segments (must be even, so the 45°
 * silhouette points are exact samples). The visible walls run from the left
 * silhouette point, round the front corner, to the right silhouette point.
 */
export function roundedSlab(b: Box, r: number, steps = 6): { top: Pt[]; left: Pt[]; right: Pt[] } {
  if (steps % 2 !== 0) throw new Error('steps must be even');
  const { x, y, z, w, d, h } = b;
  const rr = Math.max(0, Math.min(r, w / 2, d / 2));
  const arc = (cx: number, cy: number, a0: number, a1: number): Array<[number, number]> =>
    Array.from({ length: steps + 1 }, (_, i) => {
      const a = ((a0 + ((a1 - a0) * i) / steps) * Math.PI) / 180;
      return [cx + rr * Math.cos(a), cy + rr * Math.sin(a)];
    });
  // back, right, front and left corners, traversed as one continuous loop
  const back = arc(x + rr, y + rr, 180, 270);
  const right = arc(x + w - rr, y + rr, 270, 360);
  const front = arc(x + w - rr, y + d - rr, 0, 90);
  const left = arc(x + rr, y + d - rr, 90, 180);
  const half = steps / 2;
  const top = [...back, ...right, ...front, ...left].map(([px, py]) => project(px, py, z + h));
  const wall = (path: Array<[number, number]>): Pt[] => [
    ...path.map(([px, py]) => project(px, py, z + h)),
    ...[...path].reverse().map(([px, py]) => project(px, py, z)),
  ];
  return {
    top,
    left: wall([...front.slice(half), ...left.slice(0, half + 1)]),
    right: wall([...right.slice(half), ...front.slice(0, half + 1)]),
  };
}

/** Outline of the box footprint at its base: used for drop shadows. */
export function footprint(b: Box, z = b.z): Pt[] {
  return [project(b.x, b.y, z), project(b.x + b.w, b.y, z), project(b.x + b.w, b.y + b.d, z), project(b.x, b.y + b.d, z)];
}

export interface CylinderGeometry {
  /** closed path for the visible side wall */
  side: string;
  /** the top ellipse */
  top: { cx: number; cy: number; rx: number; ry: number };
  /** the base ellipse center (for shadows) */
  base: { cx: number; cy: number; rx: number; ry: number };
}

/** An upright cylinder standing on (cx, cy, z) with radius r and height h. */
export function cylinder(cx: number, cy: number, z: number, r: number, h: number): CylinderGeometry {
  const { rx, ry } = isoEllipseRadii(r);
  const [bx, by] = project(cx, cy, z);
  const [tx, ty] = project(cx, cy, z + h);
  const f = (n: number) => Math.round(n * 100) / 100;
  // left edge down, front half of the base ellipse (sweep 0 goes through the bottom), right edge up
  const side = `M${f(tx - rx)} ${f(ty)} L${f(bx - rx)} ${f(by)} A${f(rx)} ${f(ry)} 0 0 0 ${f(bx + rx)} ${f(by)} L${f(tx + rx)} ${f(ty)} Z`;
  return { side, top: { cx: f(tx), cy: f(ty), rx: f(rx), ry: f(ry) }, base: { cx: f(bx), cy: f(by), rx: f(rx), ry: f(ry) } };
}

/** A flat polyline on the plane at height z (for copper traces / wires). */
export function tracePoints(points: Array<[number, number]>, z: number): Pt[] {
  return points.map(([x, y]) => project(x, y, z));
}
