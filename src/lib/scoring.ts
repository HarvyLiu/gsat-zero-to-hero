/**
 * 學測 scoring rules for practice items. Pure functions, no DOM, shared by the item runner and tests.
 *
 * Source: 大考中心 116學年度學科能力測驗考試簡章（初版 115/8/4）三、成績計算 (一)2–3, as recorded in
 * research/verified-2026-11-15.json (key "exam-wide", status verified_primary):
 *  - 單選: all or nothing;
 *  - 多選 with n options: options are judged independently; k wrongly judged options earn (n − 2k)/n
 *    of the item's points, with a floor of 0 (and a 多選 item has at least one correct option);
 *  - 選填: every blank must be right; wrong answers are not penalised.
 *
 * Blank 多選 → 0 is official: the 116 簡章 rule (registry fact exam.multi-select-scoring) says
 * 「所得分數低於零或完全未作答者，該題以零分計」. (Closes docs/design/06-critique.md §3's open item.)
 * The item runner never lets a learner submit a blank 多選 answer, so the rule never shows in the UI.
 */

/** The minus cell on a 選填 answer sheet. U+2212 MINUS SIGN, never the ASCII hyphen. */
export const MINUS = '−';

/** The 選填 bubble alphabet, in the order the runner draws it. */
export const FILL_ALPHABET = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', MINUS] as const;

/** 單選: 1 when the chosen option is the key, else 0 (nothing chosen is 0). */
export function scoreSingle(selected: number | null | undefined, answer: number): 0 | 1 {
  return selected === answer ? 1 : 0;
}

export interface MultiJudgement {
  /** fraction of the item's points, 0..1 */
  score: number;
  /** number of options judged wrongly */
  k: number;
  n: number;
  /** selected but not in the key (誤選) */
  extra: number[];
  /** in the key but not selected (漏選) */
  missed: number[];
  /** extra ∪ missed, ascending */
  wrong: number[];
  blank: boolean;
}

function checkIndices(label: string, xs: readonly number[], n: number): void {
  for (const x of xs) {
    if (!Number.isInteger(x) || x < 0 || x >= n) throw new RangeError(`${label}: option index ${x} is outside 0..${n - 1}`);
  }
}

/**
 * 多選: judge each of the n options on its own. An option is judged wrongly when it is selected but not
 * in the key, or in the key but not selected. Score = max(0, (n − 2k)/n). Blank → 0 (see the open item above).
 */
export function judgeMulti(selected: readonly number[], answer: readonly number[], n: number): MultiJudgement {
  if (!Number.isInteger(n) || n < 1) throw new RangeError(`scoreMulti: n must be a positive integer, got ${n}`);
  checkIndices('scoreMulti answer', answer, n);
  checkIndices('scoreMulti selection', selected, n);
  if (answer.length === 0) throw new RangeError('scoreMulti: a 多選 key has at least one correct option');
  const pick = new Set(selected);
  const key = new Set(answer);
  const extra = [...pick].filter((i) => !key.has(i)).sort((a, b) => a - b);
  const missed = [...key].filter((i) => !pick.has(i)).sort((a, b) => a - b);
  const wrong = [...extra, ...missed].sort((a, b) => a - b);
  const k = wrong.length;
  const blank = pick.size === 0;
  const score = blank ? 0 : Math.max(0, (n - 2 * k) / n);
  return { score, k, n, extra, missed, wrong, blank };
}

export function scoreMulti(selected: readonly number[], answer: readonly number[], n: number): number {
  return judgeMulti(selected, answer, n).score;
}

/** Map what a learner might type for a cell onto the bubble alphabet (full-width digits, hyphens → '−'). */
export function normalizeCell(cell: string | null | undefined): string {
  if (cell == null) return '';
  const c = cell.trim();
  if (/^[−\-－‐‑‒–﹣]$/.test(c)) return MINUS;
  if (/^[０-９]$/.test(c)) return String.fromCharCode(c.charCodeAt(0) - 0xff10 + 0x30);
  return c;
}

/** 選填: 1 only when every cell matches the key (same length, '−' included), else 0. */
export function scoreFill(cells: readonly (string | null | undefined)[], answer: readonly string[]): 0 | 1 {
  if (cells.length !== answer.length) return 0;
  return answer.every((a, i) => normalizeCell(cells[i]) === a) ? 1 : 0;
}

// ---------- typed numbers (our own "numeric" items; not a 學測 item type) ----------

export type NumericAccept = 'int' | 'decimal' | 'fraction';

/** An exact rational p/q with q > 0. BigInt so that long decimals compare exactly. */
export interface Rational {
  p: bigint;
  q: bigint;
}

function gcd(a: bigint, b: bigint): bigint {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b) [a, b] = [b, a % b];
  return a;
}

function reduce(p: bigint, q: bigint): Rational {
  if (q === 0n) throw new RangeError('zero denominator');
  if (q < 0n) [p, q] = [-p, -q];
  const g = gcd(p, q) || 1n;
  return { p: p / g, q: q / g };
}

/** Full-width digits and signs (from a zh IME) to ASCII; U+2212 to '-'. */
function asciiNumber(s: string): string {
  return s
    .trim()
    .replace(/[０-９]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 0xff10 + 0x30))
    .replace(/[−－‐‑‒–﹣]/g, '-')
    .replace(/＋/g, '+')
    .replace(/[．。]/g, '.')
    .replace(/／/g, '/')
    .replace(/\s*\/\s*/g, '/');
}

const INT_RE = /^[+-]?\d+$/;
const DEC_RE = /^([+-]?)(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/;
const FRAC_RE = /^([+-]?\d+)\/(\d+)$/;

function parseDecimal(s: string): Rational | null {
  const m = DEC_RE.exec(s);
  if (!m) return null;
  const [, sign, whole = '', frac = '', exp] = m;
  if (!whole && !frac) return null;
  let p = BigInt((whole || '0') + frac) * (sign === '-' ? -1n : 1n);
  let q = 10n ** BigInt(frac.length);
  const e = exp ? Number(exp) : 0;
  if (Math.abs(e) > 400) return null;
  if (e > 0) p *= 10n ** BigInt(e);
  if (e < 0) q *= 10n ** BigInt(-e);
  return reduce(p, q);
}

/**
 * Parse a typed answer in the form an item accepts. Returns null when the text is not a number of that
 * form: 'int' takes whole numbers; 'decimal' takes whole numbers and decimals; 'fraction' takes whole
 * numbers and p/q (sign in front). Spaces around '/', full-width digits and '−' are fine.
 */
export function parseNumeric(input: string, accept: NumericAccept): Rational | null {
  const s = asciiNumber(input);
  if (!s) return null;
  if (INT_RE.test(s)) return reduce(BigInt(s), 1n);
  if (accept === 'decimal') return parseDecimal(s);
  if (accept === 'fraction') {
    const m = FRAC_RE.exec(s);
    if (!m || BigInt(m[2]) === 0n) return null;
    return reduce(BigInt(m[1]), BigInt(m[2]));
  }
  return null;
}

/** The stored key as a rational. A number key goes through its shortest decimal form, so 0.1 is exactly 1/10. */
export function keyValue(answer: number | string, accept: NumericAccept): Rational {
  const v = typeof answer === 'number' ? parseDecimal(String(answer)) : parseNumeric(answer, accept === 'int' ? 'int' : accept);
  if (!v) throw new RangeError(`numeric key ${JSON.stringify(answer)} is not a valid ${accept}`);
  return v;
}

/** 1 when the typed value equals the key (by value: 6/8 equals 3/4), 0 when not, null when unreadable. */
export function scoreNumeric(input: string, answer: number | string, accept: NumericAccept): 0 | 1 | null {
  const got = parseNumeric(input, accept);
  if (!got) return null;
  const want = keyValue(answer, accept);
  return got.p === want.p && got.q === want.q ? 1 : 0;
}

// ---------- 混合題 self-assessment ----------

/** Self-score for a written answer: points of the ticked criteria over all points (0..1). */
export function scoreRubric(met: readonly string[], criteria: readonly { id: string; points: number }[]): number {
  const total = criteria.reduce((s, c) => s + c.points, 0);
  if (total <= 0) return 0;
  const ticked = new Set(met);
  const got = criteria.reduce((s, c) => s + (ticked.has(c.id) ? c.points : 0), 0);
  return got / total;
}
