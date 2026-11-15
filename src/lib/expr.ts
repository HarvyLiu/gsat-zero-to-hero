/**
 * A tiny, safe arithmetic-expression compiler for graph widgets: authors write `a*x^2 + b` or
 * `2sin(x)` in MDX props and get a JS function — no eval, no access to anything but numbers.
 *
 * Grammar (usual precedence; ^ is right-associative and binds tighter than unary minus, so -x^2 = -(x^2)):
 *   expr   = term (('+' | '-') term)*
 *   term   = unary (('*' | '/') unary | implicit-product)*      implicit: 2x, 3(x+1), (x+1)(x-1), 2sin(x)
 *   unary  = '-' unary | '+' unary | power
 *   power  = atom ('^' unary)?
 *   atom   = number | name | name '(' expr ')' | '(' expr ')' | '|' expr '|'
 * Names: variables passed to compile(), constants pi and e, functions sin cos tan sqrt abs log (base 10) ln exp.
 */
export type Env = Record<string, number>;
export type Compiled = (env: Env) => number;

const FUNCS: Record<string, (v: number) => number> = {
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  sqrt: Math.sqrt,
  abs: Math.abs,
  log: Math.log10,
  ln: Math.log,
  exp: Math.exp,
};
const CONSTS: Record<string, number> = { pi: Math.PI, e: Math.E };

type Tok = { t: 'num'; v: number } | { t: 'name'; v: string } | { t: 'op'; v: string };

function tokenize(src: string): Tok[] {
  const out: Tok[] = [];
  const s = src.replace(/π/g, 'pi').replace(/−/g, '-').replace(/×/g, '*').replace(/÷/g, '/');
  let i = 0;
  while (i < s.length) {
    const c = s[i];
    if (/\s/.test(c)) {
      i++;
    } else if (/[0-9.]/.test(c)) {
      const m = /^\d*\.?\d+(?:e[+-]?\d+)?|^\d+\.?/.exec(s.slice(i))!;
      out.push({ t: 'num', v: Number(m[0]) });
      i += m[0].length;
    } else if (/[A-Za-z_]/.test(c)) {
      const m = /^[A-Za-z_][A-Za-z_0-9]*/.exec(s.slice(i))!;
      out.push({ t: 'name', v: m[0] });
      i += m[0].length;
    } else if ('+-*/^()|,'.includes(c)) {
      out.push({ t: 'op', v: c });
      i++;
    } else {
      throw new Error(`Unexpected character "${c}" in expression "${src}"`);
    }
  }
  return out;
}

/** Compile an expression; `vars` lists the names it may use (e.g. ['x', 'a', 'b']). */
export function compile(src: string, vars: string[] = ['x']): Compiled {
  const toks = tokenize(src);
  let p = 0;
  let absDepth = 0;
  const peek = () => toks[p];
  const isOp = (v: string) => peek()?.t === 'op' && peek()!.v === v;
  const expect = (v: string) => {
    if (!isOp(v)) throw new Error(`Expected "${v}" in expression "${src}"`);
    p++;
  };

  const expr = (): Compiled => {
    let left = term();
    while (isOp('+') || isOp('-')) {
      const op = toks[p++].v;
      const l = left;
      const r = term();
      left = op === '+' ? (e) => l(e) + r(e) : (e) => l(e) - r(e);
    }
    return left;
  };
  /** an implicit product starts where a new atom begins right after the previous one */
  const startsAtom = () => {
    const k = peek();
    if (!k) return false;
    if (k.t === 'num' || k.t === 'name') return true;
    if (k.t === 'op' && k.v === '(') return true;
    // an opening |…| only when we're not about to close one
    return k.t === 'op' && k.v === '|' && absDepth === 0;
  };
  const term = (): Compiled => {
    let left = unary();
    for (;;) {
      if (isOp('*') || isOp('/')) {
        const op = toks[p++].v;
        const l = left;
        const r = unary();
        left = op === '*' ? (e) => l(e) * r(e) : (e) => l(e) / r(e);
      } else if (startsAtom()) {
        const l = left;
        const r = power();
        left = (e) => l(e) * r(e);
      } else return left;
    }
  };
  const unary = (): Compiled => {
    if (isOp('-')) {
      p++;
      const u = unary();
      return (e) => -u(e);
    }
    if (isOp('+')) {
      p++;
      return unary();
    }
    return power();
  };
  const power = (): Compiled => {
    const base = atom();
    if (isOp('^')) {
      p++;
      const ex = unary();
      return (e) => Math.pow(base(e), ex(e));
    }
    return base;
  };
  const atom = (): Compiled => {
    const k = toks[p++];
    if (!k) throw new Error(`Unexpected end of expression "${src}"`);
    if (k.t === 'num') return () => k.v;
    if (k.t === 'op' && k.v === '(') {
      const inner = expr();
      expect(')');
      return inner;
    }
    if (k.t === 'op' && k.v === '|') {
      absDepth++;
      const inner = expr();
      absDepth--;
      expect('|');
      return (e) => Math.abs(inner(e));
    }
    if (k.t === 'name') {
      const name = k.v;
      if (name in FUNCS && isOp('(')) {
        p++;
        const arg = expr();
        expect(')');
        const f = FUNCS[name];
        return (e) => f(arg(e));
      }
      if (vars.includes(name)) return (e) => e[name];
      if (name in CONSTS) return () => CONSTS[name];
      throw new Error(`Unknown name "${name}" in expression "${src}" (allowed: ${[...vars, ...Object.keys(CONSTS)].join(', ')})`);
    }
    throw new Error(`Unexpected "${k.v}" in expression "${src}"`);
  };

  const out = expr();
  if (p < toks.length) throw new Error(`Unexpected "${toks[p].v}" in expression "${src}"`);
  return out;
}
