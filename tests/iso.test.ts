import { describe, expect, it } from 'vitest';
import { COS30, project, viewRectFor, isoEllipseRadii, toPercent, type Box } from '../src/iso/project';
import { boxFaces, cylinder } from '../src/iso/shapes';
import { isBehind, sortForDrawing } from '../src/iso/sort';
import { shade } from '../src/iso/palette';

const box = (x: number, y: number, z: number, w: number, d: number, h: number): Box => ({ x, y, z, w, d, h });

describe('project', () => {
  it('maps the origin to the origin', () => {
    expect(project(0, 0, 0)).toEqual([0, 0]);
  });
  it('sends +x right-and-down and +y left-and-down', () => {
    const [ax, ay] = project(10, 0, 0);
    const [bx, by] = project(0, 10, 0);
    expect(ax).toBeCloseTo(10 * COS30);
    expect(ay).toBeCloseTo(5);
    expect(bx).toBeCloseTo(-10 * COS30);
    expect(by).toBeCloseTo(5);
  });
  it('sends +z straight up', () => {
    expect(project(0, 0, 7)).toEqual([0, -7]);
  });
});

describe('isoEllipseRadii', () => {
  it('projects a circle to a 2:1-ish ellipse', () => {
    const { rx, ry } = isoEllipseRadii(10);
    expect(rx).toBeCloseTo(12.247, 2);
    expect(ry).toBeCloseTo(7.071, 2);
    // A point on the circle must land on the ellipse.
    const t = 0.7;
    const [sx, sy] = project(10 * Math.cos(t), 10 * Math.sin(t), 0);
    expect((sx / rx) ** 2 + (sy / ry) ** 2).toBeCloseTo(1, 6);
  });
});

describe('boxFaces', () => {
  it('returns left, right, then top with darker sides', () => {
    const faces = boxFaces(box(0, 0, 0, 10, 10, 10), '#808080');
    expect(faces.map((f) => f.side)).toEqual(['left', 'right', 'top']);
    expect(faces[2].fill).toBe('#808080');
    expect(faces[0].fill).toBe(shade('#808080', -0.15));
    expect(faces[1].fill).toBe(shade('#808080', -0.3));
  });
  it('honours colour overrides', () => {
    const faces = boxFaces(box(0, 0, 0, 1, 1, 1), '#808080', { top: '#ffffff' });
    expect(faces[2].fill).toBe('#ffffff');
  });
});

describe('shade', () => {
  it('darkens and lightens', () => {
    expect(shade('#808080', -1)).toBe('#000000');
    expect(shade('#808080', 1)).toBe('#ffffff');
    expect(shade('#fff', 0)).toBe('#ffffff');
  });
  it('rejects bad colours', () => {
    expect(() => shade('nope', 0.1)).toThrow();
  });
});

describe('cylinder', () => {
  it('puts the top ellipse h units above the base', () => {
    const c = cylinder(5, 5, 0, 3, 8);
    expect(c.base.cy - c.top.cy).toBeCloseTo(8);
    expect(c.side.startsWith('M')).toBe(true);
  });
});

describe('viewRectFor / toPercent', () => {
  it('wraps every corner with padding', () => {
    const r = viewRectFor([box(0, 0, 0, 10, 10, 10)], 5);
    expect(r.x).toBeCloseTo(-10 * COS30 - 5, 1);
    expect(r.y).toBeCloseTo(-10 - 5, 1);
    expect(toPercent([r.x, r.y], r)).toEqual({ left: 0, top: 0 });
  });
});

describe('draw order', () => {
  const board = box(0, 0, 0, 100, 100, 5);
  const chipBack = box(10, 10, 5, 20, 20, 5);
  const chipFront = box(60, 60, 5, 20, 20, 5);
  const tallBack = box(40, 0, 5, 10, 30, 40);

  it('detects simple cases', () => {
    expect(isBehind(board, chipBack)).toBe(true); // below
    expect(isBehind(chipBack, chipFront)).toBe(true); // farther on x
    expect(isBehind(chipFront, chipBack)).toBe(false);
  });

  it('paints board, then far parts, then near parts', () => {
    const sorted = sortForDrawing([chipFront, tallBack, chipBack, board], (b) => b);
    expect(sorted[0]).toBe(board);
    expect(sorted.indexOf(chipBack)).toBeLessThan(sorted.indexOf(chipFront));
    expect(sorted.indexOf(tallBack)).toBeLessThan(sorted.indexOf(chipFront));
  });

  it('stacks slabs bottom to top', () => {
    const slabs = [box(10, 10, 20, 50, 50, 8), box(0, 0, 0, 70, 70, 8), box(5, 5, 10, 60, 60, 8)];
    const sorted = sortForDrawing(slabs, (b) => b);
    expect(sorted.map((b) => b.z)).toEqual([0, 10, 20]);
  });

  it('keeps authored order when geometry does not care', () => {
    const a = box(0, 50, 0, 10, 10, 10);
    const b = box(50, 0, 0, 10, 10, 10); // separated on x and y in opposite directions
    expect(sortForDrawing([a, b], (x) => x)).toEqual([a, b]);
    expect(sortForDrawing([b, a], (x) => x)).toEqual([b, a]);
  });

  it('survives intersecting boxes', () => {
    const a = box(0, 0, 0, 10, 10, 10);
    const b = box(5, 5, 5, 10, 10, 10);
    expect(sortForDrawing([b, a], (x) => x)).toHaveLength(2);
  });
});

import { faceColors, roundedSlab } from '../src/iso/shapes';
import { contrast, luminance } from '../src/iso/palette';

describe('faceColors', () => {
  it('lightens the top of near-black parts instead of darkening their sides into black', () => {
    const dark = faceColors('#1e1e2e');
    expect(luminance(dark.top)).toBeGreaterThan(luminance('#1e1e2e'));
    expect(dark.left).toBe('#1e1e2e');
  });
  it('leaves mid tones alone', () => {
    expect(faceColors('#808080').top).toBe('#808080');
  });
});

describe('roundedSlab', () => {
  const slab = roundedSlab(box(0, 0, 0, 100, 60, 10), 8);
  it('samples every corner for the top face', () => {
    expect(slab.top).toHaveLength(4 * 7);
  });
  it('builds closed walls from the silhouette points round the front corner', () => {
    // each wall: half of one arc + half of the next, at the top and again at the bottom
    expect(slab.left).toHaveLength(2 * 8);
    expect(slab.right).toHaveLength(2 * 8);
    // the walls reach the silhouette: the leftmost and rightmost points on screen
    const xs = slab.top.map(([x]) => x);
    expect(slab.left.some(([x]) => Math.abs(x - Math.min(...xs)) < 1e-6)).toBe(true);
    expect(slab.right.some(([x]) => Math.abs(x - Math.max(...xs)) < 1e-6)).toBe(true);
  });
  it('refuses an odd number of steps', () => {
    expect(() => roundedSlab(box(0, 0, 0, 10, 10, 1), 2, 5)).toThrow();
  });
});

describe('contrast', () => {
  it('matches known WCAG ratios', () => {
    expect(contrast('#000000', '#ffffff')).toBeCloseTo(21, 5);
    expect(contrast('#ffffff', '#ffffff')).toBeCloseTo(1, 5);
  });
});
