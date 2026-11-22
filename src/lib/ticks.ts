/**
 * Axis layout helpers for Graph.tsx.
 *
 * tickStep: Mafs draws one grid line and one number per unit, which smears into a solid band on a wide
 * axis (0–1100 g/mol, 0–4200 people) and crowds a medium one (17–35 ℃ in 320 px). The step is the
 * smallest 1-2-5 value whose ticks are at least MIN_GAP px apart on an axis `px` long, never below 1, so
 * figures with up to ~17 units per 320 px keep one tick per unit and look as before.
 *
 * bottomPad: x-axis tick numbers hang below y = 0. When y = 0 is the bottom edge (or close to it), they
 * are cut off, so the view extends down by about one label height.
 */
export const MIN_GAP = 18;
const LABEL_PX = 22;

export function tickStep(span: number, px = 320): number {
  if (!(span > 0) || !(px > 0)) return 1;
  for (let p = 1; ; p *= 10) {
    for (const m of [1, 2, 5]) {
      if (((m * p) / span) * px >= MIN_GAP) return m * p;
    }
  }
}

/** The y range with room for the x-axis numbers, given the figure height in px. */
export function withBottomPad(y: [number, number], height: number): [number, number] {
  const [y0, y1] = y;
  const pad = (LABEL_PX / height) * (y1 - y0);
  // the x axis (y = 0) is visible and its numbers would fall below the bottom edge
  if (y0 <= 0 && y0 > -pad && y1 > 0) return [-pad, y1];
  return y;
}
