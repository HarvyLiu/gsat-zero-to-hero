import { describe, expect, it } from 'vitest';
import { compile } from '../../src/lib/expr';

const at = (src: string, env: Record<string, number> = {}, vars?: string[]) => compile(src, vars ?? ['x', ...Object.keys(env)])(env);

describe('expression compiler', () => {
  it('follows the usual precedence', () => {
    expect(at('1+2*3')).toBe(7);
    expect(at('(1+2)*3')).toBe(9);
    expect(at('2^3^2')).toBe(512); // right-associative
    expect(at('-x^2', { x: 3 })).toBe(-9); // -(x^2)
    expect(at('2^-1')).toBe(0.5);
  });
  it('supports implicit products', () => {
    expect(at('2x', { x: 5 })).toBe(10);
    expect(at('3(x+1)', { x: 1 })).toBe(6);
    expect(at('(x+1)(x-1)', { x: 3 })).toBe(8);
    expect(at('2sin(x)', { x: Math.PI / 2 })).toBeCloseTo(2);
    expect(at('2pi')).toBeCloseTo(2 * Math.PI);
  });
  it('knows functions, constants and absolute-value bars', () => {
    expect(at('sqrt(16)+abs(-3)')).toBe(7);
    expect(at('log(1000)')).toBeCloseTo(3);
    expect(at('ln(e)')).toBeCloseTo(1);
    expect(at('|x-3|', { x: -2 })).toBe(5);
    expect(at('2|x|+1', { x: -4 })).toBe(9);
    expect(at('π')).toBeCloseTo(Math.PI);
  });
  it('uses parameters', () => {
    expect(at('a*x^2+b', { x: 2, a: 3, b: -1 })).toBe(11);
  });
  it('rejects anything that is not arithmetic', () => {
    expect(() => compile('alert(1)')).toThrow(/Unknown name/);
    expect(() => compile('x;y')).toThrow(/Unexpected character/);
    expect(() => compile('(x+1')).toThrow(/Expected/);
    expect(() => compile('y+1')).toThrow(/Unknown name "y"/);
  });
});
