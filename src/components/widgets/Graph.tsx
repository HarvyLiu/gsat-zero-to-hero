/**
 * Interactive coordinate-plane figure (Mafs, MIT). Authors describe it with data in MDX:
 *
 *   <Graph desc="…" x={[-5, 5]} y={[-3, 7]}
 *     params={[{ name: 'a', min: -3, max: 3, value: 1 }]}
 *     functions={[{ expr: 'a*(x-1)^2 - 2', label: 'y=f(x)' }]}
 *     points={[{ at: ['1', '-2'], label: '頂點' }]} />
 *
 * Every coordinate / radius may be a number or an expression in the slider parameters, so figures
 * move with the sliders. Expressions go through src/lib/expr.ts (no eval). `desc` is required: it is
 * the text alternative for screen readers and for anyone who can't see the figure.
 */
import { useMemo, useState } from 'react';
import { Circle, Coordinates, Line, Mafs, Plot, Point, Polygon, Text, Theme, Vector } from 'mafs';
import { compile, type Env } from '../../lib/expr';
import { tickStep, withBottomPad } from '../../lib/ticks';

type Num = number | string;
export interface GraphParam {
  name: string;
  min: number;
  max: number;
  step?: number;
  value: number;
  label?: string;
}
export interface GraphProps {
  desc: string;
  x?: [number, number];
  y?: [number, number];
  height?: number;
  params?: GraphParam[];
  functions?: { expr: string; label?: string; color?: string; domain?: [number, number]; dashed?: boolean }[];
  /** curves x(t), y(t) for t in [t0, t1] (circles, ellipses, unit-circle angles, …) */
  curves?: { x: string; y: string; t: [Num, Num]; color?: string; dashed?: boolean }[];
  points?: { at: [Num, Num]; label?: string; color?: string }[];
  segments?: { from: [Num, Num]; to: [Num, Num]; color?: string; dashed?: boolean }[];
  /** a whole line through two points */
  lines?: { through: [[Num, Num], [Num, Num]]; color?: string; dashed?: boolean }[];
  vectors?: { tip: [Num, Num]; tail?: [Num, Num]; label?: string; color?: string }[];
  circles?: { center: [Num, Num]; r: Num; color?: string }[];
  polygons?: { points: [Num, Num][]; color?: string }[];
  labels?: { at: [Num, Num]; text: string; color?: string }[];
  /** keep 1 unit the same length on both axes (default: on when the figure has circles, polygons,
   *  vectors or parametric curves, so circles stay round and angles stay true) */
  equal?: boolean;
  /** draw the axes, grid and tick numbers (default true). Set false for schematic figures (apparatus,
   *  particle boxes, tables, Lewis structures), where tick numbers would collide with the labels. */
  axes?: boolean;
  /** UI language of the slider labels (passed by the island wrapper) */
  locale?: 'zh-tw' | 'en';
}

const COLORS: Record<string, string> = {
  red: 'var(--teal)',
  blue: 'var(--accent)',
  amber: 'var(--orange)',
  green: 'var(--good)',
  ink: 'var(--ink)',
};
const col = (c?: string, fallback = 'var(--accent)') => (c ? (COLORS[c] ?? c) : fallback);
// Mafs' default tick label (a hidden '-' keeps negative numbers centred), but blank outside [lo, hi]
const tickLabel = ([lo, hi]: [number, number]) => (v: number) =>
  v < lo - 1e-9 || v > hi + 1e-9 ? null : (
    <>
      {v}
      {v < 0 && <tspan visibility="hidden">-</tspan>}
    </>
  );
export default function Graph(props: GraphProps) {
  const { desc, x = [-5, 5], y = [-5, 5], height = 320, params = [] } = props;
  const [env, setEnv] = useState<Env>(() => Object.fromEntries(params.map((p) => [p.name, p.value])));
  const names = params.map((p) => p.name);
  const axes = props.axes !== false;
  const equal = props.equal ?? Boolean(props.circles?.length || props.polygons?.length || props.vectors?.length || props.curves?.length);

  // compile once; a typo throws at build (server render), so it never reaches a learner
  const num = useMemo(() => {
    const cache = new Map<string, (e: Env) => number>();
    return (v: Num, extra: string[] = []) => {
      if (typeof v === 'number') return () => v;
      const key = `${v}|${extra.join(',')}`;
      if (!cache.has(key)) cache.set(key, compile(v, [...names, ...extra]));
      return cache.get(key)!;
    };
  }, [names.join(',')]);
  const pt = (p: [Num, Num]): [number, number] => [num(p[0])(env), num(p[1])(env)];
  const fns = useMemo(() => (props.functions ?? []).map((f) => ({ ...f, fn: compile(f.expr, ['x', ...names]) })), [props.functions, names.join(',')]);

  return (
    <figure className="graph-widget">
      <div className="graph-canvas" role="img" aria-label={desc}>
        <Mafs height={height} viewBox={{ x, y: axes ? withBottomPad(y, height) : y }} preserveAspectRatio={equal ? 'contain' : false} pan={false} zoom={false}>
          {axes && (
            <Coordinates.Cartesian
              subdivisions={false}
              // Mafs pads the view (and the bottom pad adds more), so ticks just outside the author's range would get
              // half-clipped labels (e.g. −10 on a count axis, 26 above y = 25): label only ticks inside the range
              xAxis={{ lines: tickStep(x[1] - x[0]), labels: tickLabel(x) }}
              yAxis={{ lines: tickStep(y[1] - y[0], height), labels: tickLabel(y) }}
            />
          )}
          {(props.polygons ?? []).map((g, i) => (
            <Polygon key={`pg${i}`} points={g.points.map(pt)} color={col(g.color, 'var(--orange)')} fillOpacity={0.18} />
          ))}
          {(props.circles ?? []).map((c, i) => (
            <Circle key={`c${i}`} center={pt(c.center)} radius={num(c.r)(env)} color={col(c.color)} fillOpacity={0.05} />
          ))}
          {fns.map((f, i) => (
            <Plot.OfX key={`f${i}`} y={(xv) => f.fn({ ...env, x: xv })} color={col(f.color, i === 0 ? 'var(--accent)' : 'var(--teal)')} domain={f.domain} style={f.dashed ? 'dashed' : 'solid'} />
          ))}
          {(props.curves ?? []).map((c, i) => {
            const fx = num(c.x, ['t']);
            const fy = num(c.y, ['t']);
            return (
              <Plot.Parametric key={`cv${i}`} xy={(t) => [fx({ ...env, t }), fy({ ...env, t })]} domain={[num(c.t[0])(env), num(c.t[1])(env)]} color={col(c.color)} style={c.dashed ? 'dashed' : 'solid'} />
            );
          })}
          {(props.lines ?? []).map((l, i) => (
            <Line.ThroughPoints key={`l${i}`} point1={pt(l.through[0])} point2={pt(l.through[1])} color={col(l.color, 'var(--ink)')} style={l.dashed ? 'dashed' : 'solid'} />
          ))}
          {(props.segments ?? []).map((s, i) => (
            <Line.Segment key={`s${i}`} point1={pt(s.from)} point2={pt(s.to)} color={col(s.color, 'var(--ink)')} style={s.dashed ? 'dashed' : 'solid'} />
          ))}
          {(props.vectors ?? []).map((v, i) => (
            <Vector key={`v${i}`} tail={v.tail ? pt(v.tail) : [0, 0]} tip={pt(v.tip)} color={col(v.color, 'var(--teal)')} />
          ))}
          {(props.vectors ?? [])
            .filter((v) => v.label)
            .map((v, i) => {
              const tip = pt(v.tip);
              return (
                <Text key={`vl${i}`} x={tip[0]} y={tip[1]} attach="ne" size={16} color={col(v.color, 'var(--teal)')}>
                  {v.label}
                </Text>
              );
            })}
          {(props.points ?? []).map((p, i) => {
            const [px, py] = pt(p.at);
            return <Point key={`p${i}`} x={px} y={py} color={col(p.color, 'var(--teal)')} />;
          })}
          {[...(props.points ?? []).filter((p) => p.label), ...(props.labels ?? []).map((l) => ({ at: l.at, label: l.text, color: l.color }))].map((p, i) => {
            const [px, py] = pt(p.at);
            return (
              <Text key={`t${i}`} x={px} y={py} attach="ne" size={16} color={col(p.color, 'var(--ink)')}>
                {p.label}
              </Text>
            );
          })}
        </Mafs>
      </div>
      {params.length > 0 && (
        <div className="graph-params">
          {params.map((p) => (
            <label className="graph-param" key={p.name}>
              <span className="graph-param-name">
                {p.label ?? p.name} = <output>{Number(env[p.name].toFixed(3))}</output>
              </span>
              <input
                type="range"
                min={p.min}
                max={p.max}
                step={p.step ?? 0.1}
                value={env[p.name]}
                onChange={(e) => setEnv((old) => ({ ...old, [p.name]: Number(e.target.value) }))}
              />
            </label>
          ))}
        </div>
      )}
      <figcaption className="graph-desc">{desc}</figcaption>
    </figure>
  );
}

// re-exported so the island wrapper can theme Mafs without importing its CSS twice
export { Theme };
