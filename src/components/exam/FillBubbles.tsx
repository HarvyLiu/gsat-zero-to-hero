/**
 * 選填 answer bubbles: one native radio ROW per cell, bubbles read left to right like a row on the
 * answer sheet (owner note, 2026-11-15), symbols 0–9 and '−' (U+2212).
 * Native radios give the keyboard behaviour for free (Tab between cells, arrow keys within a cell);
 * typing a digit or '-' while a cell has focus marks it and moves on to the next cell.
 * Cells are never marked right or wrong one by one: 選填 is all-or-nothing, and per-cell marks would
 * give the answer away.
 */
import type { KeyboardEvent } from 'react';
import { FILL_ALPHABET, MINUS, normalizeCell } from '../../lib/scoring';

export interface FillBubblesProps {
  /** unique radio-group name prefix */
  name: string;
  cells: (string | null)[];
  onChange: (cell: number, value: string) => void;
  disabled?: boolean;
  /** accessible name of cell i (0-based), e.g. '第1格' / 'Cell 1' */
  cellLabel: (i: number) => string;
  /** accessible name of the '−' bubble */
  minusLabel: string;
  /** accessible name of the whole sheet */
  label: string;
}

export default function FillBubbles({ name, cells, onChange, disabled = false, cellLabel, minusLabel, label }: FillBubblesProps) {
  const onKey = (i: number) => (e: KeyboardEvent<HTMLFieldSetElement>) => {
    if (disabled || e.altKey || e.ctrlKey || e.metaKey) return;
    const sym = normalizeCell(e.key);
    if (!(FILL_ALPHABET as readonly string[]).includes(sym)) return;
    e.preventDefault();
    onChange(i, sym);
    const next = e.currentTarget.nextElementSibling?.querySelector<HTMLInputElement>('input');
    next?.focus();
  };

  return (
    <div className="fill-sheet" role="group" aria-label={label}>
      {cells.map((value, i) => (
        <fieldset className="fill-row" key={i} disabled={disabled} onKeyDown={onKey(i)}>
          <legend className="fill-head">
            <span aria-hidden="true">{String.fromCodePoint(0x2460 + i) /* ①②③… to match the stems */}</span>
            <span className="sr-only">{cellLabel(i)}</span>
          </legend>
          {FILL_ALPHABET.map((sym) => (
            <label className={`fill-bubble${value === sym ? ' is-marked' : ''}`} key={sym}>
              <input className="fill-input" type="radio" name={`${name}-c${i}`} value={sym} checked={value === sym} onChange={() => onChange(i, sym)} />
              <span className="fill-mark" aria-hidden="true">
                {sym}
              </span>
              <span className="sr-only">{sym === MINUS ? minusLabel : sym}</span>
            </label>
          ))}
        </fieldset>
      ))}
    </div>
  );
}
