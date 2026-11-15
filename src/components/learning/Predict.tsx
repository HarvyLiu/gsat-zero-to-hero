/**
 * Predict-then-reveal (port of ASMC Predict). The reader commits to a guess before the explanation
 * (children) is shown; being wrong costs nothing. Labels are bilingual through `locale`.
 *
 * MDX uses it through PredictIsland.astro, which hydrates it and passes `locale` and `chapter`
 * (hydration directives only work on components imported inside the MDX file itself).
 * The prompt may be a string (with **bold**, *italic*, `code`) or a named slot (slot="prompt"),
 * which is how math reaches it: KaTeX renders at build time in the slot.
 */
import { Fragment, useState, type ReactNode } from 'react';
import { progress } from '../../lib/progress';

type Locale = 'zh-tw' | 'en';

const L = {
  'zh-tw': {
    head: '先猜猜看',
    yourGuess: '你的猜測',
    lock: '確定我的猜測',
    skip: '完全沒概念，直接告訴我',
    invalid: '請輸入一個數字，亂猜也可以。',
    answerIs: '答案是',
    spotOn: '猜中了！',
    youGuessed: '你猜',
    close: '很接近了！',
    readOn: '往下讀，看看為什麼。',
    comma: '，',
    stop: '。',
  },
  en: {
    head: 'Predict first',
    yourGuess: 'Your guess',
    lock: 'Lock in my guess',
    skip: 'I have no idea, just show me',
    invalid: 'Type a number, even a wild guess.',
    answerIs: 'The answer is',
    spotOn: 'Spot on!',
    youGuessed: 'You guessed',
    close: 'So close!',
    readOn: 'Read on to see why.',
    comma: '. ',
    stop: '.',
  },
} as const satisfies Record<Locale, Record<string, string>>;

/** Accepts ASCII or full-width digits, a minus sign in any of its usual forms, and thousands separators. */
export function parseGuess(raw: string): number | null {
  const s = raw
    .trim()
    .replace(/[０-９]/g, (d) => String.fromCharCode(d.charCodeAt(0) - 0xfee0))
    .replace(/[−－‐–]/g, '-')
    .replace(/．/g, '.')
    .replace(/[,，\s]/g, '');
  if (!/^-?(\d+\.?\d*|\.\d+)$/.test(s)) return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

const RE = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*)/g;

/** Tiny inline formatter for string props: **bold**, *italic*, `code`. */
function Rich({ text }: { text: string }): ReactNode {
  return (
    <>
      {text.split(RE).map((part, i) => {
        if (!part) return null;
        if (part.startsWith('**') && part.endsWith('**') && part.length > 4) return <strong key={i}>{part.slice(2, -2)}</strong>;
        if (part.startsWith('`') && part.endsWith('`') && part.length > 2) return <code key={i}>{part.slice(1, -1)}</code>;
        if (part.startsWith('*') && part.endsWith('*') && part.length > 2) return <em key={i}>{part.slice(1, -1)}</em>;
        return <Fragment key={i}>{part}</Fragment>;
      })}
    </>
  );
}

export default function Predict({
  id,
  prompt,
  answer,
  unit,
  locale = 'zh-tw',
  chapter,
  children,
}: {
  /** unique within the chapter; stored as '<chapter>/<id>' so CompleteChapter can count it */
  id: string;
  /** a string, or (from Astro) the rendered slot="prompt" content */
  prompt?: ReactNode;
  answer: number;
  unit?: string;
  locale?: Locale;
  chapter?: string;
  children?: ReactNode;
}) {
  const l = L[locale];
  const key = chapter ? `${chapter}/${id}` : id;
  const [typed, setTyped] = useState('');
  const [guess, setGuess] = useState<number | null>(null);
  const [skipped, setSkipped] = useState(false);
  const [invalid, setInvalid] = useState(false);
  const locked = guess !== null || skipped;

  const fmt = (n: number) => n.toLocaleString(locale === 'zh-tw' ? 'zh-TW' : 'en');
  // zh text never gets typed spaces between Han and digits (cjk.css autospaces them); en needs them
  const sp = locale === 'en' ? ' ' : '';
  const withUnit = (n: number) => (
    <>
      <b>{fmt(n)}</b>
      {unit ? `${sp}${unit}` : ''}
    </>
  );

  const lock = () => {
    const v = parseGuess(typed);
    if (v === null) {
      setInvalid(true);
      return;
    }
    setInvalid(false);
    setGuess(v);
    progress().markItem(key);
  };
  const skip = () => {
    setSkipped(true);
    progress().markItem(key);
  };

  const exact = guess !== null && Math.abs(guess - answer) < 1e-9;
  const close = guess !== null && !exact && Math.abs(guess - answer) <= Math.max(1, Math.abs(answer) * 0.1);

  return (
    <section className="predict card widget">
      <header className="widget-head">
        <h3 className="label">{l.head}</h3>
      </header>
      <div className="predict-prompt">{typeof prompt === 'string' ? <Rich text={prompt} /> : prompt}</div>
      {!locked ? (
        <form
          className="quiz-typed"
          onSubmit={(e) => {
            e.preventDefault();
            lock();
          }}
        >
          <label className="sr-only" htmlFor={`${key}-guess`}>
            {l.yourGuess}
          </label>
          <input
            id={`${key}-guess`}
            className="text-input mono"
            inputMode="decimal"
            autoComplete="off"
            value={typed}
            placeholder={l.yourGuess}
            aria-invalid={invalid || undefined}
            onChange={(e) => {
              setTyped(e.target.value);
              setInvalid(false);
            }}
          />
          {unit && <span className="predict-unit">{unit}</span>}
          <button type="submit" className="btn btn-small btn-primary">
            {l.lock}
          </button>
          <button type="button" className="linklike" onClick={skip}>
            {l.skip}
          </button>
          {invalid && (
            <p className="fb fb-wrong" role="alert">
              {l.invalid}
            </p>
          )}
        </form>
      ) : (
        <p className={`predict-result fb ${exact ? 'fb-right' : 'fb-reveal'}`} aria-live="polite">
          {skipped || guess === null ? (
            <>
              {l.answerIs}
              {sp}
              {withUnit(answer)}
              {l.stop}
            </>
          ) : exact ? (
            <>
              <b>{l.spotOn}</b>
              {sp}
              {l.answerIs}
              {sp}
              {withUnit(answer)}
              {l.stop}
            </>
          ) : (
            <>
              {l.youGuessed}
              {sp}
              {fmt(guess)}
              {l.comma}
              {l.answerIs}
              {sp}
              {withUnit(answer)}
              {l.stop}
              {sp}
              {close ? l.close : l.readOn}
            </>
          )}
        </p>
      )}
      <div className="predict-reveal" hidden={!locked}>
        {children}
      </div>
    </section>
  );
}
