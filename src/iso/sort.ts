import type { Box } from './project';

/**
 * True when `a` must be painted before `b`: `a` lies entirely on the far side of `b`
 * along at least one axis (smaller x, smaller y or lower z is farther from the viewer).
 */
export function isBehind(a: Box, b: Box): boolean {
  return a.x + a.w <= b.x || a.y + a.d <= b.y || a.z + a.h <= b.z;
}

/**
 * Painter's-algorithm order for non-intersecting boxes.
 * Builds a "must draw before" graph and topologically sorts it, keeping the
 * authored order wherever the geometry doesn't care. Returns a new array.
 */
export function sortForDrawing<T>(items: T[], boxOf: (item: T) => Box): T[] {
  const n = items.length;
  const boxes = items.map(boxOf);
  const after: number[][] = Array.from({ length: n }, () => []);
  const indegree = new Array<number>(n).fill(0);

  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const iFirst = isBehind(boxes[i], boxes[j]);
      const jFirst = isBehind(boxes[j], boxes[i]);
      // If both hold, the two boxes cannot overlap on screen, so no constraint is needed.
      if (iFirst && !jFirst) {
        after[i].push(j);
        indegree[j]++;
      } else if (jFirst && !iFirst) {
        after[j].push(i);
        indegree[i]++;
      }
    }
  }

  const done = new Array<boolean>(n).fill(false);
  const order: number[] = [];
  while (order.length < n) {
    // lowest authored index whose prerequisites are all drawn
    let next = -1;
    for (let i = 0; i < n; i++) {
      if (!done[i] && indegree[i] === 0) {
        next = i;
        break;
      }
    }
    if (next === -1) {
      // A cycle means boxes intersect. Fall back to center depth for what's left.
      const rest = items
        .map((_, i) => i)
        .filter((i) => !done[i])
        .sort((a, b) => depthKey(boxes[a]) - depthKey(boxes[b]));
      next = rest[0];
    }
    done[next] = true;
    order.push(next);
    for (const k of after[next]) indegree[k]--;
  }
  return order.map((i) => items[i]);
}

function depthKey(b: Box): number {
  return b.x + b.w / 2 + (b.y + b.d / 2) + (b.z + b.h / 2);
}
