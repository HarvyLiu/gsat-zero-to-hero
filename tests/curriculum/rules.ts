/**
 * The plan's curriculum rules as pure functions over a Curriculum (src/data/curriculum.ts).
 * Each rule returns a list of human-readable violations ([] = pass), so the same rule runs on the
 * real outlines and on the fixtures in tests/fixtures/course/, where failing variants prove it fires.
 * Sources of the rules: docs/plan.md (Course architecture, Tests), docs/design/05-platform.md §6 and
 * the critic's fixes in docs/design/06-critique.md (§1 items 3, 7, 11, 19; §2; §7).
 */
import { z } from 'astro/zod';
import { isOnPath, type Chapter, type Curriculum } from '../../src/data/curriculum';
import { CodeKey, MINUTES_CAP, NEW_CONCEPT_CAP, type CodeEntry, type SourceDef, type TermEntry } from '../../src/data/schema';

export type Violations = string[];

export interface Lookups {
  /** the glossary (Builder D's src/data/glossary.ts), when it exists */
  getTerm?: (id: string) => TermEntry | undefined;
  /** the code registry (Builder A's src/data/codes.ts), when it exists */
  getCode?: (key: string) => CodeEntry | undefined;
}

export type Rule = (cur: Curriculum, lookups: Lookups) => Violations;

const fmt = (paths: string[]) => paths.join('+') || '(no path)';

/**
 * Sprint-style review chapters (kind 'review', any chapter in a sprint track — e.g. its toolbox and
 * exam-skills chapters — or any chapter that states an entry level with `assumes`) revisit material the learner studied in school, so their concepts need not be taught
 * by an ancestor; they only have to exist (glossary or some chapter).
 */
export const reviewStyle = (c: Chapter) => c.kind === 'review' || c.track.startsWith('sprint') || c.assumes.length > 0;

/** Track ids starting with "sprint" are review sets (the 116 sprint), not taught sequences. */
export const isSprintTrack = (track: string) => track.startsWith('sprint');

function introducedBy(cur: Curriculum): Map<string, string[]> {
  const out = new Map<string, string[]>();
  for (const c of cur.chapters) for (const t of c.newConcepts) out.set(t, [...(out.get(t) ?? []), c.id]);
  return out;
}

// ---------- no jumps ----------

export const NO_JUMP_RULES = {
  uniqueIds(cur) {
    const seen = new Set<string>();
    const dups: string[] = [];
    for (const c of cur.chapters) {
      if (seen.has(c.id)) dups.push(`chapter id ${c.id} is used twice`);
      seen.add(c.id);
    }
    return dups;
  },

  prereqsExist(cur) {
    return cur.chapters.flatMap((c) => c.prereqs.filter((p) => !cur.chapterById(p)).map((p) => `${c.id} needs ${p}, which does not exist`));
  },

  sameSubjectPrereqsComeEarlier(cur) {
    return cur.chapters.flatMap((c) =>
      c.prereqs
        .map((p) => cur.chapterById(p))
        .filter((d): d is Chapter => !!d && d.subject === c.subject && d.index >= c.index)
        .map((d) => `${c.id} needs ${d.id}, which comes later in ${c.subject}.json`),
    );
  },

  acyclic(cur) {
    const state = new Map<string, 'open' | 'done'>();
    const stack: string[] = [];
    const cycles: string[] = [];
    const walk = (id: string) => {
      state.set(id, 'open');
      stack.push(id);
      for (const p of cur.chapterById(id)?.prereqs ?? []) {
        if (!cur.chapterById(p)) continue;
        if (state.get(p) === 'open') cycles.push(`prereq cycle: ${[...stack.slice(stack.indexOf(p)), p].join(' needs ')}`);
        else if (!state.has(p)) walk(p);
      }
      stack.pop();
      state.set(id, 'done');
    };
    for (const c of cur.chapters) if (!state.has(c.id)) walk(c.id);
    return cycles;
  },

  everyChapterHasAPrereq(cur) {
    const firstOfTrack = new Set<Chapter>();
    const seenTracks = new Set<string>();
    for (const c of cur.chapters) {
      const key = `${c.subject}|${c.track}`;
      if (c.track !== 'core' && !seenTracks.has(key)) firstOfTrack.add(c);
      seenTracks.add(key);
    }
    return cur.chapters
      .filter((c) => c.prereqs.length === 0 && c.kind !== 'welcome' && c.kind !== 'exam-literacy' && !firstOfTrack.has(c))
      .map((c) => `${c.id} (${c.kind}) has no prerequisite`);
  },

  conceptIntroducedOnce(cur) {
    return [...introducedBy(cur)].filter(([, by]) => by.length > 1).map(([t, by]) => `concept ${t} is introduced ${by.length} times: ${by.join(', ')}`);
  },

  usesAreTaughtEarlier(cur, lk) {
    const owners = introducedBy(cur);
    const out: Violations = [];
    for (const c of cur.chapters) {
      const before = cur.ancestorsOf(c.id);
      const refs = [...c.uses.map((t) => ['uses', t] as const), ...c.reviews.map((t) => ['reviews', t] as const)];
      for (const [field, t] of refs) {
        if (lk.getTerm?.(t)?.kind === 'vocab') continue; // glossary-only words are exempt (schema TermEntry.kind)
        const by = owners.get(t);
        if (reviewStyle(c)) {
          if (!by && !lk.getTerm?.(t)) out.push(`${c.id} ${field} ${t}, which is neither in the glossary nor introduced by any chapter`);
          continue;
        }
        // A sprint review chapter re-teaches every concept it reviews (definition + examples), so a later
        // chapter that depends on it may use those concepts even though no core chapter "introduces" them yet.
        const reviewedBefore = cur.chapters.some((a) => before.has(a.id) && reviewStyle(a) && a.reviews.includes(t));
        if (reviewedBefore) continue;
        if (!by) out.push(`${c.id} ${field} ${t}, which no chapter introduces (or reviews in a prerequisite sprint chapter)`);
        else if (!c.newConcepts.includes(t) && !by.some((o) => before.has(o))) out.push(`${c.id} ${field} ${t} from ${by.join(', ')}, which it does not depend on`);
      }
    }
    return out;
  },

  newConceptCap(cur) {
    return cur.chapters.flatMap((c) => {
      const cap = NEW_CONCEPT_CAP[c.kind];
      return cap !== null && c.newConcepts.length > cap ? [`${c.id} (${c.kind}) introduces ${c.newConcepts.length} concepts; the cap is ${cap}`] : [];
    });
  },

  prereqsOnEveryPathOfTheChapter(cur) {
    const out: Violations = [];
    for (const c of cur.chapters) {
      if (c.subject === 'site') continue;
      for (const p of c.prereqs) {
        const d = cur.chapterById(p);
        if (!d || d.subject !== c.subject) continue;
        const off = c.onPaths.filter((x) => !d.onPaths.includes(x));
        if (off.length) out.push(`${c.id} (on ${fmt(c.onPaths)}) needs ${d.id}, which is not on ${fmt(off)}`);
      }
    }
    return out;
  },

  noOffPathAncestors(cur) {
    // e.g. a 數B chapter must never sit behind a 數A-only chapter, however indirectly.
    const out: Violations = [];
    for (const c of cur.chapters) {
      if (c.subject === 'site') continue;
      for (const a of cur.ancestorsOf(c.id)) {
        const d = cur.chapterById(a)!;
        if (d.subject !== c.subject) continue;
        const off = c.onPaths.filter((x) => !d.onPaths.includes(x));
        if (off.length) out.push(`${c.id} (on ${fmt(c.onPaths)}) has ancestor ${d.id}, which is only on ${fmt(d.onPaths)}`);
      }
    }
    return out;
  },

  crossSubjectPrereqsTargetSharedChapters(cur) {
    // Cross-subject edges go only into bridges or core chapters every learner of that subject takes
    // (plan: "Cross-subject edges may only point into bridge chapters or whitelisted gate chapters").
    // Site chapters (welcome, exam literacy) are shared by every subject, so they are always allowed.
    const out: Violations = [];
    for (const c of cur.chapters) {
      for (const p of c.prereqs) {
        const d = cur.chapterById(p);
        if (!d || d.subject === c.subject || d.subject === 'site') continue;
        if (d.kind !== 'bridge' && d.kind !== 'core') out.push(`${c.id} needs ${d.id} from another subject, which is a ${d.kind} chapter (only bridge or core)`);
        const off = cur.pathsOf(d.subject).filter((x) => !d.onPaths.includes(x));
        if (off.length) out.push(`${c.id} needs ${d.id} from another subject, which is not on ${fmt(off)}`);
      }
    }
    return out;
  },

  extensionsAreNeverPrereqsOfOtherKinds(cur) {
    return cur.chapters.flatMap((c) =>
      c.kind === 'extension'
        ? []
        : c.prereqs
            .map((p) => cur.chapterById(p))
            .filter((d): d is Chapter => d?.kind === 'extension')
            .map((d) => `${c.id} (${c.kind}) needs extension chapter ${d.id}`),
    );
  },

  conceptsAreInTheGlossary(cur, lk) {
    if (!lk.getTerm) return [];
    return cur.chapters.flatMap((c) =>
      [...c.newConcepts, ...c.uses, ...c.reviews].filter((t) => !lk.getTerm!(t)).map((t) => `${c.id}: ${t} is not in the glossary`),
    );
  },

  deepenedConceptsAreIntroduced(cur, lk) {
    // `deepens` marks a spiral revisit; the earlier concept must be owned by some chapter
    // (not necessarily an ancestor: math deepens 地科's 半衰期 without depending on 地科).
    if (!lk.getTerm) return [];
    const owners = introducedBy(cur);
    return cur.chapters.flatMap((c) =>
      c.newConcepts.flatMap((t) => {
        const d = lk.getTerm!(t)?.deepens;
        return d && !owners.has(d) ? [`${c.id} introduces ${t}, which deepens ${d}, but no chapter introduces ${d}`] : [];
      }),
    );
  },
} satisfies Record<string, Rule>;

// ---------- structure ----------

export const STRUCTURE_RULES = {
  partsNumberedFromZero(cur) {
    return cur.courses.flatMap((course) => {
      const nums = course.parts.map((p) => p.num);
      return nums.every((n, i) => n === i) ? [] : [`${course.subject}: parts are numbered ${nums.join(', ')}; expected 0..${nums.length - 1} in file order`];
    });
  },

  corePartsBeforeTracks(cur) {
    return cur.courses.flatMap((course) => {
      const first = course.parts.findIndex((p) => p.track !== 'core');
      if (first < 0) return [];
      return course.parts.slice(first).filter((p) => p.track === 'core').map((p) => `${course.subject}: core Part ${p.num} (${p.id}) comes after a track part`);
    });
  },

  tracksAreWellFormed(cur) {
    const out: Violations = [];
    for (const course of cur.courses) {
      let last: string | undefined;
      const closed = new Set<string>();
      for (const p of course.parts) {
        const id = p.track === 'core' ? 'core' : p.track.id;
        if (p.track !== 'core') {
          if (id === 'core') out.push(`${course.subject} Part ${p.num}: a track may not be called "core"`);
          if (closed.has(id)) out.push(`${course.subject} Part ${p.num}: track ${id} is split; its parts must be consecutive`);
          for (const a of p.track.entry.after) {
            const target = cur.chapterById(a);
            if (!target) out.push(`${course.subject} Part ${p.num}: track ${id} starts after ${a}, which does not exist`);
            else if (target.subject === course.subject && target.track === id) out.push(`${course.subject} Part ${p.num}: track ${id} starts after its own chapter ${a}`);
          }
        }
        if (last !== undefined && last !== id) closed.add(last);
        last = id;
      }
    }
    return out;
  },

  corePartsEndWithACheckpoint(cur) {
    // Every core part after Part 0 of a subject closes with a checkpoint or capstone, on every path
    // (a part that branches into 數A/數B needs one on each branch). Track parts are exempt: sprint
    // parts are review sets, and an extension part cannot end in a checkpoint without making an
    // extension chapter a prereq of a non-extension one. Site parts are orientation, not taught content.
    const out: Violations = [];
    for (const course of cur.courses) {
      if (course.subject === 'site') continue;
      const all = cur.pathsOf(course.subject);
      for (const part of course.parts) {
        if (part.track !== 'core' || part.num === 0) continue;
        for (const path of all) {
          const on = part.chapters.filter((ch) => (ch.paths ?? all).includes(path));
          const end = on.at(-1);
          if (end && end.kind !== 'checkpoint' && end.kind !== 'capstone')
            out.push(`${course.subject} Part ${part.num} (${part.id}) on ${path} ends with ${end.slug} (${end.kind}), not a checkpoint or capstone`);
        }
      }
    }
    return out;
  },

  minutesWithinCap(cur) {
    return cur.chapters.flatMap((c) => {
      const cap = MINUTES_CAP[c.kind];
      return cap !== null && c.minutes > cap ? [`${c.id} (${c.kind}) runs ${c.minutes} min; the cap is ${cap}`] : [];
    });
  },

  notExaminedMarkOnlyInExtensions(cur, lk) {
    // ※ = "suggested not in national exams" (e.g. cot/sec/csc): extension tracks only.
    const out: Violations = [];
    for (const c of cur.chapters) {
      if (c.kind === 'extension') continue;
      if (c.marks.includes('※')) out.push(`${c.id} (${c.kind}) is marked ※; only extension chapters may be`);
      for (const r of c.codes) if (lk.getCode?.(r.key)?.marks.includes('※')) out.push(`${c.id} (${c.kind}) refers to ※ code ${r.key}; only extension chapters may`);
    }
    return out;
  },

  pathsAreKnown(cur) {
    const out: Violations = [];
    for (const c of cur.chapters) {
      if (!c.paths) continue;
      if (c.subject === 'site') out.push(`${c.id}: site chapters are on every path and must not declare paths`);
      else if (c.paths.length === 0) out.push(`${c.id} declares an empty paths list (omit it for every path)`);
      else for (const p of c.paths.filter((x) => !cur.pathsOf(c.subject).includes(x))) out.push(`${c.id} is on unknown path ${p}`);
    }
    return out;
  },
} satisfies Record<string, Rule>;

// ---------- coverage ----------

const COVERING_ROLES = new Set(['teaches', 'reviews']);
/** roles that put a code "behind" a chapter for the dependsOn check (bridges teach 國中/國小 codes) */
const DEPENDENCY_ROLES = new Set(['teaches', 'reviews', 'bridges']);

export interface Coverage {
  subject: string;
  total: number;
  covered: number;
  missing: string[];
}

/** The learner paths an in-scope code must be taught on. */
export function requiredPaths(code: CodeEntry, subject: string, cur: Curriculum): string[] {
  if (code.gsatTrack === 'A') return ['mathA'];
  if (code.gsatTrack === 'B') return ['mathB'];
  return cur.pathsOf(subject);
}

/** Every inGsat 'yes' code of a subject, taught or reviewed on each path it is examined on. */
export function coverageOf(cur: Curriculum, subject: string, codes: CodeEntry[]): Coverage {
  const inScope = codes.filter((c) => c.inGsat === 'yes' && (c.subjects as string[]).includes(subject));
  const missing: string[] = [];
  for (const code of inScope) {
    // A code shared by several subjects needs one owner, in any of them.
    const refs = cur.chapters.filter(
      (ch) => ch.subject !== 'site' && (code.subjects as string[]).includes(ch.subject) && ch.codes.some((r) => r.key === code.key && COVERING_ROLES.has(r.role)),
    );
    const required = requiredPaths(code, subject, cur);
    const unknown = required.filter((p) => !cur.pathsOf(subject).includes(p));
    if (unknown.length) {
      missing.push(`${code.key} (${code.code}) has gsatTrack ${code.gsatTrack}, but ${subject} has no path ${fmt(unknown)}`);
      continue;
    }
    const off = required.filter((p) => !refs.some((ch) => isOnPath(ch, p)));
    if (off.length) missing.push(`${code.key} (${code.code}) is not taught or reviewed on ${fmt(off)}`);
  }
  return { subject, total: inScope.length, covered: inScope.length - missing.length, missing };
}

export function unknownCodeRefs(cur: Curriculum, getCode: (k: string) => CodeEntry | undefined): Violations {
  return cur.chapters.flatMap((c) => [
    ...c.codes.filter((r) => !getCode(r.key)).map((r) => `${c.id} refers to unknown code ${r.key}`),
    ...c.assumes.filter((k) => !getCode(k)).map((k) => `${c.id} assumes unknown code ${k}`),
  ]);
}

/** inGsat 'no' (分科/選修) material: only in extension chapters, or flagged with role 'beyond'. */
export function beyondScopeOutsideExtensions(cur: Curriculum, getCode: (k: string) => CodeEntry | undefined): Violations {
  return cur.chapters.flatMap((c) =>
    c.kind === 'extension'
      ? []
      : c.codes
          .filter((r) => r.role !== 'beyond' && getCode(r.key)?.inGsat === 'no')
          .map((r) => `${c.id} (${c.kind}) ${r.role} ${r.key}, which is beyond 學測; use an extension chapter or role "beyond"`),
  );
}

export interface DependencyGap {
  from: string;
  to: string;
  message: string;
}

/**
 * Code-level dependsOn (critic §2): for an official edge X → Y between codes the outline covers, some
 * chapter teaching X must have a chapter teaching Y as itself or an ancestor, or assume Y (sprint).
 */
export function dependencyGaps(cur: Curriculum, codes: CodeEntry[]): DependencyGap[] {
  const teachers = new Map<string, Chapter[]>();
  for (const c of cur.chapters) for (const r of c.codes) if (DEPENDENCY_ROLES.has(r.role)) teachers.set(r.key, [...(teachers.get(r.key) ?? []), c]);
  const gaps: DependencyGap[] = [];
  for (const x of codes) {
    const tx = teachers.get(x.key);
    if (!tx) continue;
    for (const y of x.dependsOn) {
      const ty = teachers.get(y);
      if (!ty) continue; // only between covered codes; an untaught Y is a coverage question
      const ok = tx.some((cx) => cx.assumes.includes(y) || ty.some((cy) => cy.id === cx.id || cur.ancestorsOf(cx.id).has(cy.id)));
      if (!ok)
        gaps.push({
          from: x.key,
          to: y,
          message: `${x.key} (in ${tx.map((c) => c.id).join(', ')}) depends on ${y} (in ${ty.map((c) => c.id).join(', ')}), but no chapter with ${x.key} has one with ${y} behind it`,
        });
    }
  }
  return gaps;
}

export const Waiver = z.object({ from: CodeKey, to: CodeKey, reason: z.string().min(1), approvedBy: z.string().min(1) }).strict();
export type Waiver = z.infer<typeof Waiver>;

export function applyWaivers(gaps: DependencyGap[], waivers: Waiver[]): { open: DependencyGap[]; stale: Waiver[] } {
  const key = (from: string, to: string) => `${from}→${to}`;
  const waived = new Set(waivers.map((w) => key(w.from, w.to)));
  const real = new Set(gaps.map((g) => key(g.from, g.to)));
  return { open: gaps.filter((g) => !waived.has(key(g.from, g.to))), stale: waivers.filter((w) => !real.has(key(w.from, w.to))) };
}

// ---------- sources ----------

export interface RegistryLookups {
  getSource: (id: string) => SourceDef | undefined;
  hasLicence: (id: string) => boolean;
  hasExamItem: (id: string) => boolean;
  hasMisconception: (id: string) => boolean;
}

export function sourceProblems(cur: Curriculum, reg: RegistryLookups): Violations {
  const out: Violations = [];
  for (const c of cur.chapters) {
    for (const s of c.sources) {
      const src = reg.getSource(s);
      if (!src) out.push(`${c.id} cites unknown source ${s}`);
      else {
        if (!/^https:\/\//.test(src.url)) out.push(`${c.id} cites ${s}, whose URL is not https`);
        if (!reg.hasLicence(src.licence)) out.push(`${c.id} cites ${s}, whose licence ${src.licence} is not in licences.json`);
      }
    }
    for (const e of c.examItems) if (!reg.hasExamItem(e)) out.push(`${c.id} links unknown exam item ${e}`);
    for (const m of c.misconceptions) if (!reg.hasMisconception(m)) out.push(`${c.id} lists unknown misconception ${m}`);
  }
  return out;
}

export function uncited(sources: Iterable<string>, cited: Set<string>): string[] {
  return [...sources].filter((s) => !cited.has(s));
}
