/**
 * The practice-item island (Quiz.astro renders it with client:visible).
 * Text arrives pre-rendered at build time (renderInline → KaTeX HTML), so this island ships no KaTeX.
 * Scoring follows the 學測 rules in lib/scoring.ts; results go to the progress store under locale-free
 * keys '<chapter>/<itemId>', so zh-tw and en pages share them.
 *
 * Per type: 單選 radio list + check; 多選 toggle buttons + submit, then the (n − 2k)/n score and which
 * options were judged wrongly; 選填 bubble columns (FillBubbles); typed numbers; 混合題 write → our rubric →
 * the learner ticks what they met → a self-score stored with self: true.
 * Every item: hint, explanation once answered, a tries count and "show answer". EN pages can swap any
 * item to its zh-tw text ("顯示中文 / Show in Chinese").
 */
import { useEffect, useId, useState } from 'react';
import type { Locale } from '../../data/schema';
import type { PreparedItem, PreparedText } from '../../lib/items';
import { itemKey, progress, type ItemRecord } from '../../lib/progress';
import { judgeMulti, MINUS, scoreFill, scoreNumeric, scoreRubric, scoreSingle, type MultiJudgement } from '../../lib/scoring';
import FillBubbles from './FillBubbles';

// ---------- labels (both locales; `en: Labels` makes a missing key a type error) ----------
const zh = {
  title: '練習題',
  original: '原創練習題（非大考中心試題）',
  solved: '已答對{done}／{total}',
  type: { single: '單選題', multi: '多選題', fill: '選填題', numeric: '計算題', mixed: '混合題' },
  check: '確認答案',
  submit: '提交',
  tryAgain: '再試一次',
  hint: '提示',
  hintLabel: '提示：',
  hideHint: '收起提示',
  showAnswer: '顯示答案',
  tries: '已作答{n}次',
  right: '答對了！',
  wrong: '還不對。',
  retry: '再想想看。',
  answer: '正確答案：',
  explain: '詳解：',
  pickOne: '先選一個選項。',
  multiPick: '可複選，至少選一個選項再提交。',
  multiScore: '得分比例：{formula}',
  multiAllRight: '每個選項都判斷正確！',
  multiWrong: '判斷錯誤的選項：{list}。',
  listSep: '、',
  extra: '誤選',
  missed: '漏選',
  fillLabel: '選填答案卡',
  fillCell: '第{i}格',
  fillIncomplete: '每一格都要畫記。',
  minus: '負號',
  yourAnswer: '你的答案',
  kind: { int: '整數', decimal: '數字（可含小數點）', fraction: '分數（例如3/4）' },
  unreadable: '看不懂這個答案，請輸入{kind}。',
  writeHere: '在這裡寫下你的作答（只留在這個頁面，不會送出；寫在紙上也可以）',
  revealRubric: '寫好了，對照評分重點',
  rubricTitle: '評分重點（本站自訂，非大考中心公布）',
  rubricIntro: '勾選你的作答做到的項目：',
  saveSelf: '記錄自評分數',
  selfScore: '自評：{got}／{total}分（已記錄）',
  points: '{n}分',
  model: '參考答案：',
  showZh: '顯示中文',
  showEn: '顯示英文',
  solvedBefore: '之前答對過',
  best: '目前最佳：{score}',
  selfTag: '（自評）',
};
type Labels = typeof zh;
const en: Labels = {
  title: 'Practice',
  original: 'Original practice items (not CEEC exam items)',
  solved: '{done} / {total} solved',
  type: { single: 'Single choice', multi: 'Multiple choice', fill: 'Fill-in bubbles', numeric: 'Number answer', mixed: 'Written answer' },
  check: 'Check',
  submit: 'Submit',
  tryAgain: 'Try again',
  hint: 'Hint',
  hintLabel: 'Hint: ',
  hideHint: 'Hide hint',
  showAnswer: 'Show answer',
  tries: 'Tries: {n}',
  right: 'Right!',
  wrong: 'Not quite.',
  retry: 'Have another go.',
  answer: 'Answer: ',
  explain: 'Why: ',
  pickOne: 'Pick an option first.',
  multiPick: 'Pick every option you think is right (at least one), then submit.',
  multiScore: 'Score: {formula} of the points',
  multiAllRight: 'Every option judged correctly!',
  multiWrong: 'Options judged wrongly: {list}.',
  listSep: ', ',
  extra: 'wrongly picked',
  missed: 'missed',
  fillLabel: 'Fill-in answer sheet',
  fillCell: 'Cell {i}',
  fillIncomplete: 'Mark every cell.',
  minus: 'minus sign',
  yourAnswer: 'Your answer',
  kind: { int: 'a whole number', decimal: 'a number (decimals are fine)', fraction: 'a fraction (like 3/4)' },
  unreadable: 'That doesn’t look like {kind}.',
  writeHere: 'Write your answer here (it stays on this page and is never sent; paper works too)',
  revealRubric: 'Done: compare with the marking points',
  rubricTitle: 'Marking points (ours, not published by CEEC)',
  rubricIntro: 'Tick each point your answer covers:',
  saveSelf: 'Save my self-score',
  selfScore: 'Self-score: {got} / {total} points (saved)',
  points: '{n} pt',
  model: 'Model answer: ',
  showZh: '顯示中文 / Show in Chinese',
  showEn: 'Show in English',
  solvedBefore: 'Solved before',
  best: 'Best so far: {score}',
  selfTag: ' (self-scored)',
};
export const LABELS: Record<Locale, Labels> = { 'zh-tw': zh, en };

const fill = (s: string, vars: Record<string, string | number>) => s.replace(/\{(\w+)\}/g, (_m, k: string) => String(vars[k] ?? `{${k}}`));
/** 0.6 → '0.6', 2/3 → '0.67', 1 → '1' */
export const formatScore = (x: number): string => String(Math.round(x * 100) / 100);
const optionNo = (i: number) => `(${i + 1})`;
const Html = ({ html, className, lang }: { html: string; className?: string; lang?: string }) => <span className={className} lang={lang} dangerouslySetInnerHTML={{ __html: html }} />;

/** The worked (n − 2k)/n line, with the floor at 0 spelled out. */
export function multiFormula(j: Pick<MultiJudgement, 'n' | 'k' | 'score'>): string {
  const head = `(${j.n} ${MINUS} 2×${j.k}) / ${j.n}`;
  return j.n - 2 * j.k < 0 ? `${head} < 0 → 0` : `${head} = ${formatScore(j.score)}`;
}

export interface ItemRunnerProps {
  chapter: string;
  locale: Locale;
  items: PreparedItem[];
  title?: string;
}

export default function ItemRunner({ chapter, locale, items, title }: ItemRunnerProps) {
  const L = LABELS[locale];
  const uid = useId();
  const [records, setRecords] = useState<Record<string, ItemRecord | undefined>>({});

  // read stored results after hydration, and follow changes from other islands and tabs
  useEffect(() => {
    const store = progress();
    const sync = () => setRecords(Object.fromEntries(items.map((it) => [it.id, store.item(itemKey(chapter, it.id))])));
    sync();
    return store.subscribe(sync);
  }, [chapter, items]);

  const done = items.filter((it) => (records[it.id]?.best ?? 0) >= 1).length;
  const headId = `${uid}-title`;
  return (
    <section className="quiz card widget exam-runner" aria-labelledby={headId}>
      <header className="widget-head">
        <h3 id={headId} className="label">
          {title ?? L.title}
        </h3>
        <span className={`widget-meta${done === items.length && items.length > 0 ? ' solved' : ''}`} aria-live="polite">
          {fill(L.solved, { done, total: items.length })}
        </span>
      </header>
      <p className="exam-origin">{L.original}</p>
      <ol className="quiz-list exam-list">
        {items.map((item, i) => (
          <ItemCard key={item.id} item={item} index={i} chapter={chapter} L={L} record={records[item.id]} />
        ))}
      </ol>
    </section>
  );
}

type Status = 'idle' | 'right' | 'wrong' | 'invalid' | 'incomplete' | 'scored' | 'revealed';

interface CardProps {
  item: PreparedItem;
  index: number;
  chapter: string;
  L: Labels;
  record?: ItemRecord;
}

function ItemCard({ item, index, chapter, L, record }: CardProps) {
  const uid = useId();
  const key = itemKey(chapter, item.id);
  const [status, setStatus] = useState<Status>('idle');
  const [tries, setTries] = useState(0);
  const [hintOpen, setHintOpen] = useState(false);
  const [showZh, setShowZh] = useState(false);
  const [single, setSingle] = useState<number | null>(null);
  const [multi, setMulti] = useState<number[]>([]);
  const [judged, setJudged] = useState<MultiJudgement | null>(null);
  const [cells, setCells] = useState<(string | null)[]>(() => (item.type === 'fill' ? item.answer.map(() => null) : []));
  const [typed, setTyped] = useState('');
  const [written, setWritten] = useState('');
  const [rubricOpen, setRubricOpen] = useState(false);
  const [met, setMet] = useState<string[]>([]);
  const [selfScore, setSelfScore] = useState<number | null>(null);

  const text: PreparedText = showZh && item.altHtml ? item.altHtml : item.html;
  const textLang = showZh && item.altHtml ? 'zh-TW' : undefined;
  const locked = status === 'right' || status === 'scored' || status === 'revealed';
  const nOptions = text.options?.length ?? 0;

  const attempt = (score: number, self = false) => {
    progress().recordAttempt(key, score, { self });
    setTries((t) => t + 1);
    // lets an enclosing <DialogueTurn> reveal the rest of the dialogue at once (it also listens to progress changes)
    document.getElementById(fieldsetId)?.dispatchEvent(new CustomEvent('gsat:item-answered', { bubbles: true, detail: { id: key } }));
  };
  const finish = (score: number) => {
    attempt(score);
    setStatus(score === 1 ? 'right' : 'wrong');
  };
  /** editing an answer clears the last verdict, but never unlocks a finished item */
  const edited = () => setStatus((s) => (s === 'wrong' || s === 'invalid' || s === 'incomplete' ? 'idle' : s));

  const check = () => {
    if (locked) return;
    switch (item.type) {
      case 'single':
        if (single === null) return setStatus('incomplete');
        return finish(scoreSingle(single, item.answer));
      case 'multi': {
        if (multi.length === 0) return setStatus('incomplete');
        const j = judgeMulti(multi, item.answer, nOptions);
        setJudged(j);
        attempt(j.score);
        return setStatus('scored');
      }
      case 'fill':
        if (cells.some((c) => c === null)) return setStatus('incomplete');
        return finish(scoreFill(cells, item.answer));
      case 'numeric': {
        const s = scoreNumeric(typed, item.answer, item.accept);
        if (s === null) return setStatus('invalid');
        return finish(s);
      }
      case 'mixed':
        return setRubricOpen(true);
    }
  };

  const tryAgain = () => {
    setStatus('idle');
    setJudged(null);
    setMulti([]);
    setSingle(null);
    setCells((c) => c.map(() => null));
    setTyped('');
  };

  const saveSelf = () => {
    if (item.type !== 'mixed') return;
    const s = scoreRubric(met, item.criteria);
    attempt(s, true);
    setSelfScore(s);
  };

  const answerText = () => {
    switch (item.type) {
      case 'single':
        return (
          <>
            {optionNo(item.answer)} <Html html={text.options?.[item.answer] ?? ''} lang={textLang} />
          </>
        );
      case 'multi':
        return item.answer.map(optionNo).join(L.listSep);
      case 'fill':
        return (
          <span className="fill-key">
            {item.answer.map((c, i) => (
              <span className="fill-key-cell" key={i}>
                {c}
              </span>
            ))}
          </span>
        );
      case 'numeric':
        return String(item.answer).replace(/^-/, MINUS);
      case 'mixed':
        return null;
    }
  };

  const explanation = (
    <p className="fb fb-reveal exam-explain">
      <b>{L.explain}</b>
      <Html html={text.explain} lang={textLang} />
    </p>
  );
  const fieldsetId = `${uid}-q`;
  const showExplain = status === 'right' || status === 'scored' || status === 'revealed' || (item.type === 'mixed' && rubricOpen);
  const totalPoints = item.type === 'mixed' ? item.criteria.reduce((s, c) => s + c.points, 0) : 0;
  const lastSelf = record?.attempts.at(-1)?.self === true;

  return (
    <li className={`quiz-q exam-item is-${status}${status !== 'right' && (record?.best ?? 0) >= 1 ? ' is-right' : ''}`} data-item={key}>
      <div className="exam-item-head">
        <span className="exam-type">{L.type[item.type]}</span>
        {record &&
          (record.best >= 1 ? (
            <span className="exam-record is-done">✓ {L.solvedBefore}</span>
          ) : (
            <span className="exam-record">
              {fill(L.best, { score: formatScore(record.best) })}
              {lastSelf ? L.selfTag : ''}
            </span>
          ))}
        {item.altHtml && (
          <button type="button" className="linklike exam-zh-toggle" aria-pressed={showZh} onClick={() => setShowZh((v) => !v)}>
            {showZh ? L.showEn : L.showZh}
          </button>
        )}
      </div>

      <form
        className="exam-form"
        noValidate
        onSubmit={(e) => {
          e.preventDefault();
          check();
        }}
      >
        <fieldset className="exam-fieldset" id={fieldsetId} disabled={locked}>
          <legend className="quiz-prompt exam-stem">
            <span className="sr-only">{index + 1}. </span>
            <Html html={text.stem} lang={textLang} />
          </legend>

          {item.type === 'single' && (
            <div className="quiz-options">
              {text.options?.map((opt, k) => {
                const mark = status === 'revealed' && k === item.answer ? ' right' : single === k ? (status === 'right' ? ' right' : status === 'wrong' ? ' wrong' : ' chosen') : '';
                return (
                  <label key={k} className={`quiz-option exam-choice${mark}`}>
                    <input
                      className="exam-input"
                      type="radio"
                      name={`${uid}-single`}
                      checked={single === k}
                      onChange={() => {
                        setSingle(k);
                        edited();
                      }}
                    />
                    <span className="quiz-letter">{k + 1}</span>
                    <Html html={opt} lang={textLang} />
                  </label>
                );
              })}
            </div>
          )}

          {item.type === 'multi' && (
            <>
              <p className="exam-help">{L.multiPick}</p>
              <div className="quiz-options">
                {text.options?.map((opt, k) => {
                  const on = multi.includes(k);
                  const inKey = item.answer.includes(k);
                  const shown = status === 'scored' || status === 'revealed';
                  const verdict = !shown ? '' : status === 'revealed' ? (inKey ? 'right' : '') : judged?.extra.includes(k) ? 'wrong' : judged?.missed.includes(k) ? 'missed' : on ? 'right' : '';
                  return (
                    <button
                      key={k}
                      type="button"
                      className={`quiz-option exam-toggle${on ? ' is-on' : ''}${verdict ? ` ${verdict}` : ''}`}
                      aria-pressed={on}
                      onClick={() => {
                        setMulti((m) => (m.includes(k) ? m.filter((x) => x !== k) : [...m, k].sort((a, b) => a - b)));
                        edited();
                      }}
                    >
                      <span className="quiz-letter" aria-hidden="true">
                        {on ? '✓' : k + 1}
                      </span>
                      <span className="sr-only">{optionNo(k)} </span>
                      <Html html={opt} lang={textLang} />
                      {verdict === 'wrong' && <span className="exam-mark is-wrong">{L.extra}</span>}
                      {verdict === 'missed' && <span className="exam-mark is-missed">{L.missed}</span>}
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {item.type === 'fill' && (
            <FillBubbles
              name={`${uid}-fill`}
              cells={cells}
              disabled={locked}
              label={L.fillLabel}
              cellLabel={(i) => fill(L.fillCell, { i: i + 1 })}
              minusLabel={L.minus}
              onChange={(i, v) => {
                setCells((c) => c.map((x, j) => (j === i ? v : x)));
                edited();
              }}
            />
          )}

          {item.type === 'numeric' && (
            <div className="quiz-typed">
              <label className="sr-only" htmlFor={`${uid}-num`}>
                {L.yourAnswer}
              </label>
              <input
                id={`${uid}-num`}
                className="text-input mono"
                inputMode="text"
                autoComplete="off"
                spellCheck={false}
                placeholder={L.kind[item.accept]}
                aria-invalid={status === 'invalid'}
                value={typed}
                onChange={(e) => {
                  setTyped(e.target.value);
                  edited();
                }}
              />
            </div>
          )}

          {item.type === 'mixed' && (
            <div className="exam-written">
              <label className="exam-help" htmlFor={`${uid}-text`}>
                {L.writeHere}
              </label>
              <textarea id={`${uid}-text`} className="text-input exam-textarea" rows={5} value={written} onChange={(e) => setWritten(e.target.value)} />
            </div>
          )}
        </fieldset>

        {item.type === 'mixed' && rubricOpen && (
          <fieldset className="exam-rubric">
            <legend className="exam-rubric-title">{L.rubricTitle}</legend>
            <p className="exam-help">{L.rubricIntro}</p>
            {item.criteria.map((c, k) => (
              <label key={c.id} className="exam-criterion">
                <input
                  type="checkbox"
                  checked={met.includes(c.id)}
                  onChange={(e) => {
                    const on = e.target.checked;
                    setMet((m) => (on ? [...m, c.id] : m.filter((x) => x !== c.id)));
                    setSelfScore(null);
                  }}
                />
                <Html html={text.criteria?.[k] ?? ''} lang={textLang} />
                <span className="exam-points">{fill(L.points, { n: c.points })}</span>
              </label>
            ))}
            <div className="exam-model">
              <b>{L.model}</b>
              <Html html={text.model ?? ''} lang={textLang} />
            </div>
          </fieldset>
        )}

        <div className="exam-actions">
          {item.type === 'mixed' ? (
            rubricOpen ? (
              <button type="button" className="btn btn-small btn-primary" onClick={saveSelf}>
                {L.saveSelf}
              </button>
            ) : (
              <button type="submit" className="btn btn-small btn-primary">
                {L.revealRubric}
              </button>
            )
          ) : locked ? (
            status !== 'right' && (
              <button type="button" className="btn btn-small" onClick={tryAgain}>
                {L.tryAgain}
              </button>
            )
          ) : (
            <button type="submit" className="btn btn-small btn-primary" disabled={item.type === 'multi' && multi.length === 0}>
              {item.type === 'multi' ? L.submit : L.check}
            </button>
          )}
          {text.hint && !locked && (
            <button type="button" className="btn btn-small" aria-expanded={hintOpen} aria-controls={`${uid}-hint`} onClick={() => setHintOpen((v) => !v)}>
              {hintOpen ? L.hideHint : L.hint}
            </button>
          )}
          {item.type !== 'mixed' && !locked && tries > 0 && (
            <button type="button" className="linklike" onClick={() => setStatus('revealed')}>
              {L.showAnswer}
            </button>
          )}
          {tries > 0 && <span className="exam-tries">{fill(L.tries, { n: tries })}</span>}
        </div>
      </form>

      {text.hint && hintOpen && !locked && (
        <p className="exam-hint" id={`${uid}-hint`}>
          <b>{L.hintLabel}</b>
          <Html html={text.hint} lang={textLang} />
        </p>
      )}

      <div className="exam-feedback" aria-live="polite">
        {status === 'incomplete' && <p className="fb fb-wrong">{item.type === 'fill' ? L.fillIncomplete : item.type === 'multi' ? L.multiPick : L.pickOne}</p>}
        {status === 'invalid' && item.type === 'numeric' && <p className="fb fb-wrong">{fill(L.unreadable, { kind: L.kind[item.accept] })}</p>}
        {status === 'right' && (
          <p className="fb fb-right">
            <b>{L.right}</b>
          </p>
        )}
        {status === 'wrong' && (
          <p className="fb fb-wrong">
            <b>{L.wrong}</b> {text.hint ? <Html html={text.hint} lang={textLang} /> : L.retry}
          </p>
        )}
        {status === 'scored' && judged && (
          <p className={`fb ${judged.score === 1 ? 'fb-right' : 'fb-wrong'}`}>
            <b>{fill(L.multiScore, { formula: multiFormula(judged) })}</b>{' '}
            {judged.k === 0 ? L.multiAllRight : fill(L.multiWrong, { list: judged.wrong.map(optionNo).join(L.listSep) })}
          </p>
        )}
        {(status === 'revealed' || (status === 'scored' && judged && judged.score < 1)) && item.type !== 'mixed' && (
          <p className="fb fb-reveal">
            <b>{L.answer}</b>
            {answerText()}
          </p>
        )}
        {item.type === 'mixed' && selfScore !== null && (
          <p className="fb fb-right">
            <b>{fill(L.selfScore, { got: formatScore(selfScore * totalPoints), total: totalPoints })}</b>
          </p>
        )}
        {showExplain && explanation}
      </div>
    </li>
  );
}
