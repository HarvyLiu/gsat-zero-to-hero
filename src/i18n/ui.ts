/**
 * Every UI string, in both languages. `satisfies Parity` makes a missing key a type error,
 * and tests/i18n.test.ts checks that no string is empty. t() throws instead of falling back,
 * so a gap can never ship silently.
 * The brand name is a PLACEHOLDER until the owner chooses one (docs/plan.md, owner action items).
 */
import type { Locale } from '../data/characters.ts';

export type { Locale };
export const LOCALES: Locale[] = ['zh-tw', 'en'];
export const HTML_LANG: Record<Locale, string> = { 'zh-tw': 'zh-TW', en: 'en' };
/** each language named in its own script, so a reader who can't read the current page still finds theirs */
export const LANG_NAME: Record<Locale, string> = { 'zh-tw': '中文（台灣）', en: 'English' };

const zh = {
  'site.name': '學測從零開始',
  'site.tagline': '免費、雙語、從零到學測：數學、自然、社會、國文（測試版）。',
  'site.skip': '跳到主要內容',
  'nav.home': '首頁',
  'nav.subjects': '科目',
  'nav.exam': '學測資訊',
  'nav.search': '搜尋',
  'nav.review': '複習',
  'nav.about': '關於',
  'nav.theme': '切換深色／淺色主題',
  'nav.lang': '切換語言',
  'footer.license': '課文以 CC BY-NC-SA 4.0 授權，程式碼以 MIT 授權；第三方內容依其原授權。',
  'footer.progress': '你的學習進度只存在這個瀏覽器裡。',
  'footer.report': '回報錯誤',
  'footer.about': '關於本站與資料來源',
  'chapter.minutes': '約 {n} 分鐘',
  'chapter.goals': '這一章你會學到',
  'chapter.aha': '核心觀念',
  'chapter.draft': '草稿：尚未通過查證流程，請勿當作正式內容。',
  'chapter.lastVerified': '最後查證',
  'chapter.sources': '資料來源',
  'chapter.outline': '課程大綱',
  'chapter.prev': '上一章',
  'chapter.next': '下一章',
  'learn.studentAsks': '學生提問',
  'learn.tryIt': '動手試試',
  'learn.yourTurn': '換你了',
  'learn.yourTurnHint': '先回答這一題，對話才會繼續。',
  'learn.skip': '先跳過',
  'chooser.title': '選擇語言',
  'chooser.lead': '學測從零開始：免費的雙語學測課程。',
  'home.subjects': '科目',
  'home.status.pilot': '試行中',
  'home.status.active': '開放中',
  'home.status.beta': '測試版',
  'home.status.planned': '籌備中',
  'home.sprint': '116 學測衝刺',
  'home.countdown': '距離 116 學測',
  'common.days': '天',
} as const;

type Key = keyof typeof zh;
type Parity = Record<Locale, Record<Key, string>>;

export const UI = {
  'zh-tw': zh,
  en: {
    'site.name': 'GSAT from Zero',
    'site.tagline': 'A free, bilingual course from zero to Taiwan’s GSAT (學測): Math, Science, Social Studies, Chinese (beta).',
    'site.skip': 'Skip to content',
    'nav.home': 'Home',
    'nav.subjects': 'Subjects',
    'nav.exam': 'About the GSAT',
    'nav.search': 'Search',
    'nav.review': 'Review',
    'nav.about': 'About',
    'nav.theme': 'Switch between light and dark theme',
    'nav.lang': 'Change language',
    'footer.license': 'Lessons are CC BY-NC-SA 4.0 and code is MIT; third-party material keeps its own licence.',
    'footer.progress': 'Your progress is stored only in this browser.',
    'footer.report': 'Report an error',
    'footer.about': 'About this site and its sources',
    'chapter.minutes': 'About {n} minutes',
    'chapter.goals': 'In this chapter you will',
    'chapter.aha': 'The big idea',
    'chapter.draft': 'Draft: this chapter has not passed verification yet. Do not rely on it.',
    'chapter.lastVerified': 'Last verified',
    'chapter.sources': 'Sources',
    'chapter.outline': 'Course outline',
    'chapter.prev': 'Previous',
    'chapter.next': 'Next',
    'learn.studentAsks': 'Student asks',
    'learn.tryIt': 'Try it',
    'learn.yourTurn': 'Your turn',
    'learn.yourTurnHint': 'Answer this first and the conversation continues.',
    'learn.skip': 'Skip for now',
    'chooser.title': 'Choose your language',
    'chooser.lead': 'GSAT from Zero: a free, bilingual course for Taiwan’s 學測.',
    'home.subjects': 'Subjects',
    'home.status.pilot': 'Pilot',
    'home.status.active': 'Open',
    'home.status.beta': 'Beta',
    'home.status.planned': 'Coming later',
    'home.sprint': 'GSAT 116 sprint',
    'home.countdown': 'Until the 116 GSAT',
    'common.days': 'days',
  },
} satisfies Parity;

export type UiKey = Key;

export function t(locale: Locale, key: UiKey, vars: Record<string, string | number> = {}): string {
  const s = UI[locale]?.[key];
  if (!s) throw new Error(`Missing UI string "${key}" for ${locale}`);
  return s.replace(/\{(\w+)\}/g, (_m, k: string) => String(vars[k] ?? `{${k}}`));
}
