import { describe, expect, it } from 'vitest';
import { FILL_ALPHABET, judgeMulti, MINUS, normalizeCell, parseNumeric, scoreFill, scoreMulti, scoreNumeric, scoreRubric, scoreSingle } from '../../src/lib/scoring';

describe('scoreSingle (單選: all or nothing)', () => {
  it('scores the key 1 and anything else 0', () => {
    expect(scoreSingle(2, 2)).toBe(1);
    expect(scoreSingle(1, 2)).toBe(0);
    expect(scoreSingle(null, 2)).toBe(0);
    expect(scoreSingle(undefined, 0)).toBe(0);
  });
});

describe('scoreMulti (多選: (n − 2k)/n, floor 0)', () => {
  const key = [0, 2]; // options (1) and (3) are correct, n = 5
  it('n = 5: 0 wrong → 1, 1 wrong → 0.6, 2 wrong → 0.2, ≥3 wrong → 0', () => {
    expect(scoreMulti([0, 2], key, 5)).toBe(1);
    expect(scoreMulti([0], key, 5)).toBeCloseTo(0.6); // missed (3)
    expect(scoreMulti([0, 2, 4], key, 5)).toBeCloseTo(0.6); // extra (5)
    expect(scoreMulti([0, 4], key, 5)).toBeCloseTo(0.2); // missed (3), extra (5)
    expect(scoreMulti([1, 3, 4], key, 5)).toBe(0); // all five judged wrongly
    expect(scoreMulti([0, 1, 3], key, 5)).toBe(0); // k = 3: (5 − 6)/5 < 0 → 0
    expect(scoreMulti([2, 1, 3, 4], key, 5)).toBe(0); // k = 4
  });

  it('a blank answer scores 0 (our reading; see the open item in scoring.ts)', () => {
    expect(scoreMulti([], key, 5)).toBe(0);
    // without the rule, a blank on a one-correct-option item would be k = 1 → 0.6
    expect(scoreMulti([], [3], 5)).toBe(0);
    expect(judgeMulti([], [3], 5).blank).toBe(true);
  });

  it('judges options independently and reports which ones were wrong', () => {
    const j = judgeMulti([4, 0], key, 5);
    expect(j).toMatchObject({ k: 2, n: 5, extra: [4], missed: [2], wrong: [2, 4], blank: false });
    expect(j.score).toBeCloseTo(0.2);
  });

  it('ignores duplicate selections and works for other n', () => {
    expect(scoreMulti([0, 0, 2], key, 5)).toBe(1);
    expect(scoreMulti([0], [0, 1], 4)).toBeCloseTo(0.5); // (4 − 2)/4
    expect(scoreMulti([0, 1], [0], 6)).toBeCloseTo(4 / 6);
  });

  it('rejects impossible input', () => {
    expect(() => scoreMulti([5], key, 5)).toThrow(RangeError);
    expect(() => scoreMulti([0], [7], 5)).toThrow(RangeError);
    expect(() => scoreMulti([0], [], 5)).toThrow(RangeError);
    expect(() => scoreMulti([0], [0], 0)).toThrow(RangeError);
  });
});

describe('scoreFill (選填: every cell right)', () => {
  it('uses U+2212 as the minus cell', () => {
    expect(MINUS).toBe('−');
    expect(FILL_ALPHABET).toHaveLength(11);
    expect(FILL_ALPHABET.at(-1)).toBe('−');
  });

  it('is all or nothing, including the minus cell', () => {
    const key = ['−', '1', '2'];
    expect(scoreFill(['−', '1', '2'], key)).toBe(1);
    expect(scoreFill(['−', '1', '3'], key)).toBe(0);
    expect(scoreFill(['0', '1', '2'], key)).toBe(0); // sign cell wrong
    expect(scoreFill(['1', '2'], key)).toBe(0); // too short
    expect(scoreFill(['−', '1', null], key)).toBe(0); // a blank cell
    expect(scoreFill(['−', '1', '2', '0'], key)).toBe(0);
  });

  it('accepts typed look-alikes for the minus sign and full-width digits', () => {
    expect(normalizeCell('-')).toBe(MINUS);
    expect(normalizeCell('－')).toBe(MINUS);
    expect(normalizeCell('７')).toBe('7');
    expect(scoreFill(['-', '１', '2'], ['−', '1', '2'])).toBe(1);
  });
});

describe('numeric answers', () => {
  it('parses by the accepted form', () => {
    expect(parseNumeric('42', 'int')).toEqual({ p: 42n, q: 1n });
    expect(parseNumeric('−3', 'int')).toEqual({ p: -3n, q: 1n });
    expect(parseNumeric('0.5', 'int')).toBeNull();
    expect(parseNumeric('0.250', 'decimal')).toEqual({ p: 1n, q: 4n });
    expect(parseNumeric('.5', 'decimal')).toEqual({ p: 1n, q: 2n });
    expect(parseNumeric('６／８', 'fraction')).toEqual({ p: 3n, q: 4n });
    expect(parseNumeric('-3 / 4', 'fraction')).toEqual({ p: -3n, q: 4n });
    expect(parseNumeric('3/0', 'fraction')).toBeNull();
    expect(parseNumeric('abc', 'decimal')).toBeNull();
    expect(parseNumeric('', 'int')).toBeNull();
  });

  it('compares by exact value and returns null for unreadable input', () => {
    expect(scoreNumeric('0.1', 0.1, 'decimal')).toBe(1);
    expect(scoreNumeric('0.10', '0.1', 'decimal')).toBe(1);
    expect(scoreNumeric('0.3', 0.1 + 0.2, 'decimal')).toBe(0); // the key is the float 0.30000000000000004
    expect(scoreNumeric('6/8', '3/4', 'fraction')).toBe(1);
    expect(scoreNumeric('3/5', '3/4', 'fraction')).toBe(0);
    expect(scoreNumeric('7', 7, 'int')).toBe(1);
    expect(scoreNumeric('seven', 7, 'int')).toBeNull();
  });
});

describe('scoreRubric (混合題 self-score)', () => {
  const criteria = [
    { id: 'setup', points: 2 },
    { id: 'result', points: 1 },
    { id: 'units', points: 1 },
  ];
  it('is ticked points over total points', () => {
    expect(scoreRubric([], criteria)).toBe(0);
    expect(scoreRubric(['setup'], criteria)).toBe(0.5);
    expect(scoreRubric(['setup', 'result', 'units'], criteria)).toBe(1);
    expect(scoreRubric(['nope'], criteria)).toBe(0);
  });
});
