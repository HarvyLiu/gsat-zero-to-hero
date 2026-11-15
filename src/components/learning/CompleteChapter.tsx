/**
 * "Mark chapter complete" toggle at the end of every chapter (port of ASMC CompleteChapter).
 * Progress keys are language-neutral chapter ids ('math/real-numbers'), so finishing a chapter in
 * one language marks it in the other too. Solved pieces are counted by the '<chapter>/' prefix.
 */
import { useEffect, useState } from 'react';
import { progress } from '../../lib/progress';

type Locale = 'zh-tw' | 'en';

const L = {
  'zh-tw': {
    done: '本章完成',
    ask: '讀完了嗎？',
    // no typed spaces around the digits: cjk.css autospaces Han and Latin/digits
    solved: (n: number) => `你在這一章完成了${n}個互動題。`,
    local: '你的學習進度只存在這個瀏覽器裡。',
    mark: '標記為完成',
    marked: '✓ 已完成',
    markLabel: (title: string) => `將「${title}」標記為完成`,
    unmarkLabel: (title: string) => `取消「${title}」的完成標記`,
  },
  en: {
    done: 'Chapter complete',
    ask: 'Finished reading?',
    solved: (n: number) => `You've solved ${n} interactive ${n === 1 ? 'piece' : 'pieces'} in this chapter.`,
    local: 'Your progress is saved in this browser only.',
    mark: 'Mark complete',
    marked: '✓ Completed',
    markLabel: (title: string) => `Mark ${title} as complete`,
    unmarkLabel: (title: string) => `Mark ${title} as not complete`,
  },
} as const;

export default function CompleteChapter({ id, title, locale = 'zh-tw' }: { id: string; title: string; locale?: Locale }) {
  const l = L[locale];
  const [done, setDone] = useState(false);
  const [solved, setSolved] = useState(0);

  useEffect(() => {
    const store = progress();
    const sync = () => {
      setDone(store.isChapterDone(id));
      setSolved(store.countItems(`${id}/`));
    };
    sync();
    return store.subscribe(sync);
  }, [id]);

  return (
    <div className={`complete card${done ? ' is-done' : ''}`}>
      <div>
        <p className="label">{done ? l.done : l.ask}</p>
        <p className="complete-meta">{solved > 0 ? l.solved(solved) : l.local}</p>
      </div>
      <button
        type="button"
        className={`btn ${done ? '' : 'btn-primary'}`}
        aria-pressed={done}
        onClick={() => progress().markChapter(id, !done)}
        aria-label={done ? l.unmarkLabel(title) : l.markLabel(title)}
      >
        {done ? l.marked : l.mark}
      </button>
    </div>
  );
}
