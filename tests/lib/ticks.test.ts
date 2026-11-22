import { describe, expect, it } from 'vitest';
import { MIN_GAP, tickStep, withBottomPad } from '../../src/lib/ticks';

describe('tickStep', () => {
  it('keeps one tick per unit on small spans, so existing small figures are unchanged', () => {
    for (const span of [1, 6, 10, 14, 17]) expect(tickStep(span)).toBe(1);
  });
  it('uses a 1-2-5 step on crowded or wide axes', () => {
    expect(tickStep(18)).toBe(2); // 17–35 ℃ in 320 px
    expect(tickStep(70)).toBe(5);
    expect(tickStep(140)).toBe(10);
    expect(tickStep(1100)).toBe(100);
    expect(tickStep(4200)).toBe(500);
  });
  it('keeps ticks at least MIN_GAP px apart and never wastes a step', () => {
    for (let span = 1; span < 100000; span *= 1.37) {
      const s = tickStep(span, 320);
      expect((s / span) * 320).toBeGreaterThanOrEqual(MIN_GAP);
      if (s > 1) expect((s / 2.5 / span) * 320).toBeLessThan(MIN_GAP);
    }
  });
});

describe('withBottomPad', () => {
  it('extends the view below y = 0 when the x axis sits on the bottom edge', () => {
    const [y0, y1] = withBottomPad([0, 140], 320);
    expect(y0).toBeLessThan(0);
    expect(y1).toBe(140);
  });
  it('leaves ranges alone when there is already room or the x axis is off-screen', () => {
    expect(withBottomPad([-5, 5], 320)).toEqual([-5, 5]);
    expect(withBottomPad([17, 35], 320)).toEqual([17, 35]);
  });
});
