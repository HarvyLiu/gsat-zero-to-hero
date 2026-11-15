#!/usr/bin/env node
/**
 * Imports the official 108課綱 curriculum codes from the frozen research into
 * src/data/registry/codes/<domain>.json (one CodeEntry per code, sorted by key).
 *
 * Source: research/verified-2026-11-15.json, verification side only ("verification" wins over
 * "research"): final_units (curriculum_codes, title, in_gsat, gsat_track, key_concepts, depends_on,
 * status, source_url) and final_bridging_prereqs (as inGsat 'background').
 *
 * Why a script and not hand-written JSON: the research code strings are not uniform (docs/design/
 * 05-platform.md §1.4) and the registry must be re-derivable from the frozen research. It handles:
 *  - Roman numerals Ⅰ–Ⅴ (U+2160–U+2164) vs ASCII I/V: keys are ASCII, `code` keeps the form the
 *    research gives (the 課綱 itself mixes them: physics prints Ⅴ, chemistry mostly ASCII V);
 *  - ranges 'PEb-Ⅴa-1~9', 'A-7-2~A-7-4', slashes 'Ab-Ⅱ-3/Ab-Ⅲ-3', '公Ab-Ⅳ-1/2';
 *  - subject prefixes 歷/地/公 (with or without a space), context words 數學/自然/國小/國中;
 *  - annotations '(printed …)', '(woven in …)' and prose in depends_on;
 *  - free-text entries: 探究與實作 strands and sub-items (inq:*), 田野實察 (geo:field-1..3),
 *    考試說明 objectives (exam:*), 國文 附錄四 推薦選文 (chi:sel-1..15).
 * Anything it cannot map is printed as UNMAPPED; the run fails unless overrides.json acknowledges it.
 * Manual corrections live in overrides.json (applied last), never in the generated files.
 *
 * Deterministic and idempotent: same research + overrides → byte-identical files.
 * Run: npm run import:codes
 * tests/registry/codes.test.ts re-runs buildRegistry() and checks the files are up to date.
 */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
export const RESEARCH_PATH = join(ROOT, 'research', 'verified-2026-11-15.json');
export const OUT_DIR = join(ROOT, 'src', 'data', 'registry', 'codes');
export const OVERRIDES_PATH = join(OUT_DIR, 'overrides.json');
export const RESEARCH_SOURCE = 'research:verified-2026-11-15';

/** Same order as schema.DOMAINS; one output file per domain. */
export const DOMAINS = ['math', 'nat', 'soc-elem', 'hist', 'geo', 'civ', 'chi', 'inq', 'exam'];
const SUBJECT_ORDER = ['math', 'physics', 'chemistry', 'biology', 'earth', 'inquiry', 'history', 'geography', 'civics', 'chinese'];
const MARK_ORDER = ['★', '＃', '※'];
const FIELD_ORDER = ['key', 'code', 'domain', 'subjects', 'level', 'inGsat', 'gsatTrack', 'marks', 'title', 'keyConcepts', 'dependsOn', 'status', 'source'];
const STATUSES = new Set(['verified', 'corrected', 'added', 'unverified']);
const IN_GSAT = new Set(['yes', 'partial', 'no']);
/** When a code is listed in several units, the most in-scope listing decides inGsat/gsatTrack. */
const RANK = { yes: 3, partial: 2, no: 1, unknown: 0 };

/** research key → SubjectId ('earth-inquiry' splits: its 探究/考試說明 units belong to 'inquiry'). */
const RESEARCH_SUBJECTS = { math: 'math', physics: 'physics', chemistry: 'chemistry', biology: 'biology', 'earth-inquiry': 'earth', history: 'history', geography: 'geography', civics: 'civics', chinese: 'chinese' };
const SCIENCE = new Set(['physics', 'chemistry', 'biology', 'earth', 'inquiry']);
const SOCIAL = { history: 'hist', geography: 'geo', civics: 'civ' };
const PREFIX_DOMAIN = { 歷: 'hist', 地: 'geo', 公: 'civ' };

// ---------- normalisation ----------

const ROMAN = { Ⅰ: 'I', Ⅱ: 'II', Ⅲ: 'III', Ⅳ: 'IV', Ⅴ: 'V' };
/** Ⅴ (U+2164) etc. → ASCII. */
export const asciiRoman = (s) => s.replace(/[ⅠⅡⅢⅣⅤ]/gu, (c) => ROMAN[c]);
/**
 * Key form of a code body: ASCII Roman numerals, and 數學 12甲/12乙 → 12jia/12yi, because
 * schema.CodeKey is ASCII-only (the display form keeps 甲/乙).
 */
export const asciiBody = (body) => asciiRoman(body).replace(/甲/g, 'jia').replace(/乙/g, 'yi');

/** Numeric-aware, code-point-based comparison (N-3-9 < N-3-11), independent of locale/ICU. */
export function naturalCompare(a, b) {
  const pa = a.match(/\d+|\D+/g) ?? [];
  const pb = b.match(/\d+|\D+/g) ?? [];
  for (let i = 0; i < Math.min(pa.length, pb.length); i++) {
    const x = pa[i];
    const y = pb[i];
    if (/^\d/.test(x) && /^\d/.test(y)) {
      const d = Number(x) - Number(y) || x.length - y.length;
      if (d) return d;
    } else if (x !== y) return x < y ? -1 : 1;
  }
  return pa.length - pb.length;
}

// ---------- code tokens ----------

const STAGE = '(?:Ⅴ|Ⅳ|Ⅲ|Ⅱ|Ⅰ|IV|III|II|I|V)';
/** 數學 學習內容: 主題-年級-流水號, e.g. N-10-1, S-11A-1, N-12甲-2, R-4-1 */
const MATH_BODY = '[NSGARFD]-\\d{1,2}(?:A|B|甲|乙)?-\\d+';
/**
 * Stage-coded bodies: 自然 PKa-Ⅴc-1 / INa-Ⅲ-10 / ti-Ⅴc-1, 社會 Ba-Ⅴ-1 / A-Ⅴ-1 / 1c-Ⅳ-1,
 * 國文 Ab-Ⅴ-1 / 4-Ⅴ-1, 數學 學習表現 n-III-9; serial optional (item level '地 Ba-Ⅳ', '公Aa-Ⅴ'),
 * '*' = wildcard.
 */
const STAGE_BODY = `(?:[A-Z]{1,3}[a-z]?|[a-z]{1,2}|\\d[a-z]?)-${STAGE}[ac]?(?:-(?:\\d+|\\*))?`;
const TOKEN_SRC = `(?<![A-Za-z0-9])(?:([歷地公])\\s?)?(${MATH_BODY}|${STAGE_BODY})(?![A-Za-z0-9])`;
const MATH_RE = new RegExp(`^${MATH_BODY}$`, 'u');
const CONTEXT_WORDS = /數學|自然|國小|國中/gu;

/** The serial is the '-n' after a grade (數學 N-10-1) or a stage (PKa-Ⅴc-1); without one ('Ba-Ⅳ') the code is item-level. */
const SERIAL_RE = new RegExp(`^(.*-(?:\\d{1,2}(?:A|B|甲|乙)?|${STAGE}[ac]?))-(\\d+|\\*)$`, 'u');
const splitBody = (body) => {
  const m = SERIAL_RE.exec(body);
  return m ? { family: m[1], serial: m[2] === '*' ? '*' : Number(m[2]) } : { family: body, serial: null };
};

/** ASCII stage of a body ('I'…'V'), or null for 數學 學習內容 codes (they carry a grade). */
const stageOf = (asciiB) => (MATH_RE.test(asciiB) ? null : (/^[^-]+-(IV|III|II|I|V)/.exec(asciiB)?.[1] ?? null));

/**
 * Finds every code token in `text`, with its range/slash continuations, in order.
 * `ctx` carries context words (數學/自然 force a domain; 國小 marks 國小 社會) across tokens and
 * across the segments of one string ('數學 S-6-2 地圖比例尺, n-III-9 比例').
 */
function scanTokens(text, ctx) {
  const out = [];
  const re = new RegExp(TOKEN_SRC, 'gu');
  const sticky = new RegExp(TOKEN_SRC, 'uy');
  let prevEnd = 0;
  for (let m = re.exec(text); m; m = re.exec(text)) {
    for (const w of text.slice(prevEnd, m.index).match(CONTEXT_WORDS) ?? []) {
      if (w === '數學') ctx.domain = 'math';
      else if (w === '自然') ctx.domain = 'nat';
      else ctx.elem = w === '國小';
    }
    const prefix = m[1] ?? null;
    const first = { prefix, body: m[2], ...splitBody(m[2]) };
    const parts = [first];
    let end = m.index + m[0].length;
    let bad = null;
    // continuations: '~9', '~A-7-4', '/2', '/D-7-2', ' / Cb-Ⅲ-1'
    for (;;) {
      const c = /^\s*([~～/])\s*/u.exec(text.slice(end));
      if (!c) break;
      const at = end + c[0].length;
      sticky.lastIndex = at;
      const t = sticky.exec(text);
      const n = t ? null : /^\d+/.exec(text.slice(at));
      if (!t && !n) break;
      const last = parts[parts.length - 1];
      const next = t ? { prefix: t[1] ?? prefix, body: t[2], ...splitBody(t[2]) } : null;
      if (c[1] === '/') {
        if (next) parts.push(next);
        else if (typeof last.serial === 'number') parts.push({ prefix: last.prefix, body: `${last.family}-${n[0]}`, family: last.family, serial: Number(n[0]) });
        else break;
      } else {
        const to = next ? next.serial : Number(n[0]);
        if (typeof last.serial !== 'number' || typeof to !== 'number' || (next && asciiRoman(next.family) !== asciiRoman(last.family)) || to < last.serial) {
          bad = text.slice(m.index, at + (t ? t[0].length : n[0].length));
        } else {
          for (let s = last.serial + 1; s <= to; s++) parts.push({ prefix: last.prefix, body: `${last.family}-${s}`, family: last.family, serial: s });
        }
      }
      end = at + (t ? t[0].length : n[0].length);
    }
    out.push({ start: m.index, end, parts, ctx: { ...ctx }, bad, raw: text.slice(m.index, end) });
    if (prefix) ctx.domain = PREFIX_DOMAIN[prefix];
    prevEnd = end;
    re.lastIndex = end;
  }
  return out;
}

/** Resolves a token part to a domain, key and display form. */
function resolvePart(part, ctx, subject) {
  const ab = asciiBody(part.body);
  let domain;
  if (part.prefix) domain = PREFIX_DOMAIN[part.prefix];
  else if (MATH_RE.test(part.body)) domain = 'math';
  else if (ctx.domain) domain = ctx.domain;
  else if (SCIENCE.has(subject)) domain = 'nat';
  else if (subject === 'math') domain = 'math';
  else if (subject === 'chinese') domain = 'chi';
  else domain = SOCIAL[subject];
  // 國小 社會 is one integrated subject with no 歷/地/公 prefix, so stage Ⅰ–Ⅲ social codes are soc-elem.
  if (!part.prefix && ['hist', 'geo', 'civ'].includes(domain) && (ctx.elem || ['I', 'II', 'III'].includes(stageOf(ab)))) domain = 'soc-elem';
  const display = (part.prefix && PREFIX_DOMAIN[part.prefix] === domain ? part.prefix : '') + part.body;
  const fam = asciiBody(part.family);
  return { key: `${domain}:${ab}`, domain, display, asciiBody: ab, asciiFamily: fam, serial: part.serial };
}

const stripParens = (s) => {
  let prev;
  do {
    prev = s;
    s = s.replace(/\([^()]*\)|（[^（）]*）/gu, ' ');
  } while (s !== prev);
  return s;
};
const parenContents = (s) => [...s.matchAll(/\(([^()]*)\)|（([^（）]*)）/gu)].map((m) => m[1] ?? m[2]);

/** Every code in a curriculum_codes string (annotations in parentheses are ignored unless they hold the only codes). */
export function codesInString(raw) {
  const ctx = { domain: null, elem: false };
  let toks = scanTokens(stripParens(raw), ctx);
  if (!toks.length) toks = parenContents(raw).flatMap((p) => scanTokens(p, ctx));
  return toks;
}

const LABEL_WORDS = /\b(?:bridging|bridge)\b/giu;
const isListLead = (s) => !/[A-Za-z0-9]/.test(s.replace(LABEL_WORDS, '').replace(CONTEXT_WORDS, ''));
const isConnector = (s) => /^(?:\s|and|&|及|與|和|、|國中|國小|數學|自然)*$/u.test(s);

/**
 * Codes a depends_on string really depends on. Only the leading code list of each segment counts,
 * so prose such as "…because Mb-Ⅴ-1 comes later" or "The report's Ba-Ⅳ-3 is wrong" adds nothing.
 */
export function depTokensInString(raw) {
  const ctx = { domain: null, elem: false };
  const take = (text) => {
    const out = [];
    for (const seg of text.split(/[,，;；、]|\.\s/u)) {
      const toks = scanTokens(seg, ctx);
      if (!toks.length || !isListLead(seg.slice(0, toks[0].start))) continue;
      out.push(toks[0]);
      for (let i = 1; i < toks.length && isConnector(seg.slice(toks[i - 1].end, toks[i].start)); i++) out.push(toks[i]);
    }
    return out;
  };
  const head = take(stripParens(raw));
  return head.length ? head : parenContents(raw).flatMap(take);
}

// ---------- free-text handlers ----------

/** 自然科學探究與實作: 4 strands and 14 sub-items (zh as printed in the research; en from the research unit titles). */
export const INQ_STRANDS = [
  { slug: 'discover', zh: '發現問題', en: 'Finding problems', subs: [['觀察現象', 'observe', 'Observing phenomena'], ['蒐集資訊', 'gather-info', 'Gathering information'], ['形成或訂定問題', 'pose-question', 'Framing or defining questions'], ['提出可驗證的觀點', 'testable-claim', 'Proposing testable claims']] },
  { slug: 'plan', zh: '規劃與研究', en: 'Planning and investigating', subs: [['尋找變因或條件', 'find-variables', 'Finding variables or conditions'], ['擬定研究計畫', 'draft-plan', 'Drafting a research plan'], ['收集資料數據', 'collect-data', 'Collecting data']] },
  { slug: 'argue-model', zh: '論證與建模', en: 'Argumentation and modelling', subs: [['分析資料和呈現證據', 'analyse-evidence', 'Analysing data and presenting evidence'], ['解釋和推理', 'explain-reason', 'Explaining and reasoning'], ['提出結論或解決方案', 'conclude', 'Proposing conclusions or solutions'], ['建立模型', 'build-model', 'Building models']] },
  { slug: 'share', zh: '表達與分享', en: 'Communicating and sharing', subs: [['表達與溝通', 'communicate', 'Expressing and communicating'], ['合作與討論', 'collaborate', 'Collaborating and discussing'], ['評價與省思', 'evaluate-reflect', 'Evaluating and reflecting']] },
];

function inqCodes(raw, unmapped) {
  const out = [];
  for (const s of INQ_STRANDS) {
    const i = raw.indexOf(s.zh);
    if (i < 0) continue;
    out.push({ key: `inq:${s.slug}`, domain: 'inq', display: `探究與實作：${s.zh}`, title: { 'zh-tw': s.zh, en: s.en }, level: '必修' });
    const list = /^\s*（([^）]*)）/u.exec(raw.slice(i + s.zh.length));
    for (const item of list ? list[1].split('、') : []) {
      const sub = s.subs.find(([zh]) => zh === item.trim());
      if (!sub) unmapped.push({ id: raw, kind: 'inq-subitem', note: `unknown sub-item 「${item.trim()}」 under ${s.zh}` });
      else out.push({ key: `inq:${s.slug}/${sub[1]}`, domain: 'inq', display: `探究與實作：${s.zh}／${sub[0]}`, title: { 'zh-tw': sub[0], en: sub[2] }, level: '必修' });
    }
  }
  return out;
}

const DASH = '[–~～-]';
/** 考試說明 objectives: 國文 'A1', 'B1–B5' → exam:chi-*; 自然 '測驗目標 2a–2c, 5a' → exam:nat-*. */
function examCodes(raw, subject, unmapped) {
  const out = [];
  const add = (key, display) => out.push({ key, domain: 'exam', display, level: '考試說明' });
  if (subject === 'chinese') {
    for (const m of raw.matchAll(new RegExp(`考試說明\\s*([AB])(\\d)(?:\\s*${DASH}\\s*[AB]?(\\d))?`, 'gu'))) {
      for (let n = Number(m[2]); n <= Number(m[3] ?? m[2]); n++) add(`exam:chi-${m[1]}${n}`, `考試說明${m[1]}${n}`);
    }
  } else if (SCIENCE.has(subject)) {
    const m = /考試說明\s*測驗目標\s*(.+)$/u.exec(raw);
    for (const item of m ? m[1].split(/[,，、]\s*/u) : []) {
      const r = new RegExp(`^(\\d)([a-z])(?:\\s*${DASH}\\s*(\\d)?([a-z]))?$`, 'u').exec(item.trim());
      if (!r || (r[3] && r[3] !== r[1])) {
        unmapped.push({ id: raw, kind: 'exam', note: `cannot read objective 「${item.trim()}」` });
        continue;
      }
      for (let c = r[2].charCodeAt(0); c <= (r[4] ?? r[2]).charCodeAt(0); c++) {
        const obj = `${r[1]}${String.fromCharCode(c)}`;
        add(`exam:nat-${obj}`, `考試說明 測驗目標 ${obj}`);
      }
    }
  }
  return out;
}

const CN_NUM = ['一', '二', '三', '四', '五'];

// ---------- research → registry ----------

/** The SubjectId a unit's codes belong to. */
function subjectOfUnit(researchKey, unit) {
  const base = RESEARCH_SUBJECTS[researchKey];
  if (!SCIENCE.has(base) || unit.in_gsat === 'no') return base;
  // The cross-subject 自然科學探究與實作 course (and earth-inquiry's 考試說明 skills unit) is its own subject.
  return /探究|考試說明/u.test(`${unit.title_zh} ${(unit.curriculum_codes ?? []).join(' ')}`) ? 'inquiry' : base;
}

function levelOf(domain, ab, inGsat) {
  if (domain === 'math') {
    const m = /^[NSGARFD]-(\d{1,2})(A|B|jia|yi)?-/.exec(ab);
    if (m) {
      const g = Number(m[1]);
      if (g <= 6) return `國小${g}`;
      if (g <= 9) return `國中${g}`;
      if (g === 12) return m[2] === 'yi' ? '12乙' : '12甲';
      return `${g}${m[2] ?? ''}`;
    }
  }
  const stage = /^[^-]+-(IV|III|II|I|V)([ac])?/.exec(ab);
  if (!stage) return 'unknown';
  // 學習階段: Ⅰ 國小1–2, Ⅱ 國小3–4, Ⅲ 國小5–6, Ⅳ 國中, Ⅴ 高中 (Ⅴc 部定必修, Ⅴa 加深加廣選修)
  switch (stage[1]) {
    case 'I': return '國小1–2';
    case 'II': return '國小3–4';
    case 'III': return '國小5–6';
    case 'IV': return '國中';
    default: return stage[2] === 'a' || inGsat === 'no' ? '選修' : '必修';
  }
}

function mapTrack(subject, track, inGsat) {
  if (inGsat === 'no') return 'none';
  if (subject !== 'math') return 'both';
  if (track === '數A') return 'A';
  if (track === '數B') return 'B';
  if (/^none/.test(track ?? '')) return 'none';
  return 'both';
}

const marksInTitle = (title) => [...(/（([★＃※]+)）/u.exec(title)?.[1] ?? '')];

/**
 * Builds the registry from the parsed research JSON and overrides array. Pure: no file access.
 * @param {{result: Array<{key: string, verification: any}>}} research
 * @param {Array<Record<string, any>>} overrides
 */
export function buildRegistry(research, overrides = []) {
  /** @type {Map<string, {key: string, code: string, domain: string, asciiBody?: string, asciiFamily?: string, special?: any, occ: any[]}>} */
  const acc = new Map();
  const unmapped = [];
  const partMarks = [];
  const droppedDeps = [];
  const codelessBridges = [];
  const codelessUnits = [];
  const add = (code, occ) => {
    let a = acc.get(code.key);
    if (!a) {
      a = { key: code.key, code: code.display, domain: code.domain, asciiBody: code.asciiBody, asciiFamily: code.asciiFamily, special: code.title || code.level ? { title: code.title, level: code.level } : undefined, occ: [] };
      acc.set(code.key, a);
    }
    a.occ.push(occ);
  };
  const subjects = research.result.filter((r) => RESEARCH_SUBJECTS[r.key] && r.verification?.final_units);

  // 1) units, in research order (the first listing of a code is its primary: display form, title, status, source)
  for (const r of subjects) {
    const units = [...r.verification.final_units].sort((a, b) => a.order - b.order);
    let field = 0;
    for (const unit of units) {
      const subject = subjectOfUnit(r.key, unit);
      const where = `${r.key} unit ${unit.order}`;
      if (!(unit.curriculum_codes ?? []).length) codelessUnits.push({ where, title: unit.title_zh, inGsat: unit.in_gsat });
      const inGsat = IN_GSAT.has(unit.in_gsat) ? unit.in_gsat : 'unknown';
      const status = STATUSES.has(unit.status) ? unit.status : 'unverified';
      const source = typeof unit.source_url === 'string' && unit.source_url.startsWith('https://') ? unit.source_url : RESEARCH_SOURCE;
      const title = { 'zh-tw': unit.title_zh, ...(unit.title_en ? { en: unit.title_en } : {}) };
      const marks = r.key === 'math' ? marksInTitle(unit.title_zh) : [];
      const codes = [];
      for (const raw of unit.curriculum_codes ?? []) {
        const found = [];
        if (subject === 'inquiry') found.push(...inqCodes(raw, unmapped));
        found.push(...examCodes(raw, subject, unmapped));
        if (subject === 'geography' && /田野實察/u.test(raw)) {
          field += 1;
          found.push({ key: `geo:field-${field}`, domain: 'geo', display: `田野實察（${CN_NUM[field - 1]}）`, level: '必修' });
        }
        const sel = subject === 'chinese' ? /附錄四\s*項次(\d+)/u.exec(raw) : null;
        if (sel) found.push({ key: `chi:sel-${sel[1]}`, domain: 'chi', display: `附錄四 項次${sel[1]}`, level: '必修' });
        for (const tok of codesInString(raw)) {
          if (tok.bad) unmapped.push({ id: raw, kind: 'range', note: `cannot expand 「${tok.bad}」`, where });
          for (const part of tok.parts) {
            if (part.serial === '*') {
              // A wildcard cannot be expanded from the research; keep only the members the unit cites by name.
              const fam = resolvePart(part, tok.ctx, subject);
              const cited = new Map();
              for (const k of unit.key_concepts ?? []) {
                for (const t of scanTokens(k, { domain: null, elem: false })) for (const p of t.parts) {
                  const c = resolvePart(p, t.ctx, subject);
                  if (c.asciiFamily === fam.asciiFamily && typeof c.serial === 'number') cited.set(c.key, c);
                }
              }
              found.push(...cited.values());
              unmapped.push({ id: raw, kind: 'wildcard', note: `expanded only to the cited ${[...cited.keys()].join(', ') || '(none)'}`, where });
            } else found.push(resolvePart(part, tok.ctx, subject));
          }
        }
        if (!found.length) unmapped.push({ id: raw, kind: 'code-string', note: 'no code in string', where });
        codes.push(...found);
      }

      // key concepts: a concept naming some of the unit's codes goes to those codes; the rest go to all.
      const bodies = new Set(codes.filter((c) => c.asciiBody).map((c) => c.asciiBody));
      const named = (unit.key_concepts ?? []).map((k) => {
        const s = new Set();
        for (const t of scanTokens(k, { domain: null, elem: false })) for (const p of t.parts) if (bodies.has(asciiBody(p.body))) s.add(asciiBody(p.body));
        return s;
      });
      const conceptsFor = (c) => (unit.key_concepts ?? []).filter((_, i) => named[i].size === 0 || (c.asciiBody && named[i].has(c.asciiBody)));

      // depends_on: code-like tokens only; free text (unit titles, 'Unit 3', 'Math bridge: …') is left out.
      const deps = [];
      for (const raw of unit.depends_on ?? []) {
        const toks = depTokensInString(raw);
        if (!toks.length) droppedDeps.push({ where, raw });
        for (const t of toks) for (const p of t.parts) deps.push({ ...resolvePart(p, t.ctx, subject), raw, where });
      }

      // part-level marks (★/＃/※ on part of a code) cannot be set on the code: record them.
      if (r.key === 'math') {
        for (const k of unit.key_concepts ?? []) {
          const extra = [...new Set(k.match(/[★＃※]/gu) ?? [])].filter((mk) => !marks.includes(mk));
          if (extra.length) partMarks.push({ keys: codes.map((c) => c.key), marks: extra, concept: k });
        }
      }

      const track = mapTrack(subject, unit.gsat_track, inGsat);
      const seen = new Set();
      for (const c of codes) {
        if (seen.has(c.key)) continue;
        seen.add(c.key);
        add(c, { kind: 'unit', subject, where, inGsat, gsatTrack: track, marks, title, concepts: conceptsFor(c), deps, status, source });
      }
    }
  }

  // 2) bridging prereqs (after all units, so a code a unit lists keeps that unit's data)
  for (const r of subjects) {
    for (const [i, b] of (r.verification.final_bridging_prereqs ?? []).entries()) {
      const subject = RESEARCH_SUBJECTS[r.key];
      const where = `${r.key} bridge ${i + 1}`;
      if (!(b.curriculum_codes ?? []).length) codelessBridges.push({ where, topic: b.topic_zh, status: b.status });
      const title = { 'zh-tw': b.topic_zh, ...(b.topic_en ? { en: b.topic_en } : {}) };
      const status = STATUSES.has(b.status) ? b.status : 'unverified';
      for (const raw of b.curriculum_codes ?? []) {
        const toks = codesInString(raw);
        if (!toks.length) unmapped.push({ id: raw, kind: 'code-string', note: 'no code in bridge string', where });
        for (const tok of toks) {
          if (tok.bad) unmapped.push({ id: raw, kind: 'range', note: `cannot expand 「${tok.bad}」`, where });
          for (const part of tok.parts) {
            if (part.serial === '*') {
              unmapped.push({ id: raw, kind: 'wildcard', note: 'wildcard in a bridge', where });
              continue;
            }
            add(resolvePart(part, tok.ctx, subject), { kind: 'bridge', subject, where, inGsat: 'background', gsatTrack: 'both', marks: [], title, concepts: [], deps: [], status, source: RESEARCH_SOURCE });
          }
        }
      }
    }
  }

  // 3) finalise entries
  const entries = new Map();
  for (const a of acc.values()) {
    const units = a.occ.filter((o) => o.kind === 'unit');
    const primary = a.occ[0];
    const best = units.length ? units.reduce((b, o) => (RANK[o.inGsat] > RANK[b.inGsat] ? o : b)) : primary;
    const marks = new Set(units.flatMap((o) => o.marks));
    // subjects = the syllabi that list the code: the units' subjects when a unit lists it. A bridge in
    // another subject citing it (chemistry citing 數學 N-10-1) is a dependency, not a listing, and is
    // kept in that subject's dependsOn instead. Background-only codes take every citing subject
    // (國中 自然 codes serve several sciences).
    const owners = units.length ? units : a.occ;
    entries.set(a.key, {
      key: a.key,
      code: a.code,
      domain: a.domain,
      subjects: SUBJECT_ORDER.filter((s) => owners.some((o) => o.subject === s)),
      level: a.special?.level ?? levelOf(a.domain, a.asciiBody ?? '', best.inGsat),
      inGsat: best.inGsat,
      gsatTrack: best.gsatTrack,
      marks: MARK_ORDER.filter((m) => marks.has(m)),
      title: a.special?.title ?? primary.title,
      keyConcepts: [...new Set(units.flatMap((o) => o.concepts))],
      dependsOn: [],
      status: primary.status,
      source: primary.source,
    });
  }

  // 4) dependsOn (needs every key): exact key → item-level parent ('地 Ba-Ⅳ') → item expansion ('公Aa-Ⅴ' → its codes)
  const itemLevelDeps = [];
  const missingDeps = new Map();
  for (const a of acc.values()) {
    const keys = new Set();
    for (const o of a.occ) {
      for (const d of o.deps) {
        let found = [];
        if (entries.has(d.key)) found = [d.key];
        else if (d.serial === null) {
          const pre = `${d.domain}:${d.asciiFamily}-`;
          found = [...entries.keys()].filter((k) => k.startsWith(pre) && /^\d+$/.test(k.slice(pre.length)));
        } else if (entries.has(`${d.domain}:${d.asciiFamily}`)) {
          found = [`${d.domain}:${d.asciiFamily}`];
          itemLevelDeps.push({ from: d.key, to: found[0], where: d.where });
        }
        if (!found.length) {
          const m = missingDeps.get(d.key) ?? { id: d.key, kind: 'missing-dep', note: 'cited in depends_on but not in the registry', where: new Set(), raw: new Set() };
          m.where.add(d.where);
          m.raw.add(d.raw);
          missingDeps.set(d.key, m);
        }
        for (const k of found) if (k !== a.key) keys.add(k);
      }
    }
    entries.get(a.key).dependsOn = [...keys].sort(naturalCompare);
  }
  for (const m of missingDeps.values()) unmapped.push({ ...m, where: [...m.where].join('; '), raw: [...m.raw].join(' | ') });

  // 5) overrides, applied last: {key, reason, ...fields} patches (or creates) an entry, {key, remove: true}
  //    deletes one, and `raw` lists the UNMAPPED ids (strings, or keys for missing deps) it accounts for.
  const applied = [];
  const acknowledged = new Set();
  for (const [i, o] of overrides.entries()) {
    if (!o || typeof o.reason !== 'string' || !o.reason.trim()) throw new Error(`overrides.json[${i}] needs a non-empty "reason"`);
    for (const r of [o.raw ?? []].flat()) acknowledged.add(r);
    if (!o.key) continue;
    const { key, reason, raw: _raw, remove, ...patch } = o;
    if (remove) {
      applied.push({ key, action: entries.delete(key) ? 'removed' : 'remove: no such key', reason });
      continue;
    }
    const cur = entries.get(key);
    const merged = { ...(cur ?? { key, domain: key.slice(0, key.indexOf(':')) }), ...patch };
    entries.set(key, Object.fromEntries([...FIELD_ORDER.filter((f) => f in merged).map((f) => [f, merged[f]]), ...Object.entries(merged).filter(([f]) => !FIELD_ORDER.includes(f))]));
    applied.push({ key, action: cur ? `patched ${Object.keys(patch).join(', ')}` : 'created', reason });
  }

  // dependsOn must point at real entries after overrides too
  for (const e of entries.values()) {
    for (const d of e.dependsOn ?? []) if (!entries.has(d)) unmapped.push({ id: d, kind: 'missing-dep', note: `dependsOn of ${e.key} after overrides`, where: e.key });
  }

  const ids = new Set(unmapped.map((u) => u.id));
  const domains = Object.fromEntries(DOMAINS.map((d) => [d, [...entries.values()].filter((e) => e.domain === d).sort((x, y) => naturalCompare(x.key, y.key))]));
  return {
    domains,
    unmapped: unmapped.map((u) => ({ ...u, acknowledged: acknowledged.has(u.id) })),
    stale: [...acknowledged].filter((r) => !ids.has(r)),
    applied,
    partMarks,
    droppedDeps,
    itemLevelDeps,
    codelessBridges,
    codelessUnits,
    strayDomains: [...entries.values()].filter((e) => !DOMAINS.includes(e.domain)).map((e) => e.key),
  };
}

/** File text for one domain (stable formatting, trailing newline). */
export const serialise = (list) => `${JSON.stringify(list, null, 2)}\n`;

export const readJson = (path) => JSON.parse(readFileSync(path, 'utf8'));

async function validateWithSchema(all) {
  // Node ≥ 22.18 strips TypeScript types, so the real schema can be used; older Node skips (the test validates).
  try {
    const { CodeEntry } = await import(pathToFileURL(join(ROOT, 'src', 'data', 'schema.ts')).href);
    return all.flatMap((e) => {
      const r = CodeEntry.safeParse(e);
      return r.success ? [] : [`${e.key}: ${r.error.issues.map((i) => `${i.path.join('.')} ${i.message}`).join('; ')}`];
    });
  } catch (err) {
    console.warn(`(schema validation skipped: ${err instanceof Error ? err.message : err}; npm test validates)`);
    return [];
  }
}

async function main() {
  const out = buildRegistry(readJson(RESEARCH_PATH), readJson(OVERRIDES_PATH));
  const all = Object.values(out.domains).flat();
  const invalid = await validateWithSchema(all);

  mkdirSync(OUT_DIR, { recursive: true });
  for (const d of DOMAINS) writeFileSync(join(OUT_DIR, `${d}.json`), serialise(out.domains[d]));

  const log = (s = '') => console.log(s);
  log('import-codes: research/verified-2026-11-15.json → src/data/registry/codes/');
  for (const d of DOMAINS) {
    const list = out.domains[d];
    const by = (v) => list.filter((e) => e.inGsat === v).length;
    log(`  ${d.padEnd(9)} ${String(list.length).padStart(4)}  (yes ${by('yes')}, partial ${by('partial')}, no ${by('no')}, background ${by('background')}, unknown ${by('unknown')})`);
  }
  log(`  total     ${String(all.length).padStart(4)}`);
  log();
  log(`UNMAPPED (${out.unmapped.length}):`);
  for (const u of out.unmapped) log(`  [${u.acknowledged ? 'override' : 'NO OVERRIDE'}] ${u.kind}: ${JSON.stringify(u.id)} (${u.where}) — ${u.note}${u.raw ? ` — from ${u.raw}` : ''}`);
  log();
  log(`OVERRIDES APPLIED (${out.applied.length}):`);
  for (const a of out.applied) log(`  ${a.key}: ${a.action} — ${a.reason}`);
  log();
  log(`PART-LEVEL MARKS not set on the code (express them with CodeRef.part) (${out.partMarks.length}):`);
  for (const p of out.partMarks) log(`  ${p.keys.join(', ')} ${p.marks.join('')}: ${p.concept}`);
  log();
  log(`depends_on resolved to an item-level code: ${out.itemLevelDeps.length}; free-text depends_on left out: ${out.droppedDeps.length}`);
  log(`units with no codes: ${out.codelessUnits.length}; bridges with no codes: ${out.codelessBridges.length}`);
  for (const u of out.codelessUnits) log(`  unit without codes: ${u.where} ${u.title} (in_gsat ${u.inGsat})`);
  for (const b of out.codelessBridges) log(`  bridge without codes: ${b.where} ${b.topic} (${b.status})`);

  const failures = [];
  const missing = out.unmapped.filter((u) => !u.acknowledged);
  if (missing.length) failures.push(`${missing.length} unmapped string(s) have no override`);
  if (out.stale.length) failures.push(`stale override raw id(s): ${out.stale.join(' | ')}`);
  if (invalid.length) failures.push(`schema errors:\n  ${invalid.join('\n  ')}`);
  if (out.strayDomains.length) failures.push(`entries with an unknown domain: ${out.strayDomains.join(', ')}`);
  if (failures.length) {
    console.error(`\nimport-codes FAILED: ${failures.join('; ')}`);
    process.exitCode = 1;
  }
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : '';
if (invokedPath && invokedPath.toLowerCase() === fileURLToPath(import.meta.url).toLowerCase()) await main();
