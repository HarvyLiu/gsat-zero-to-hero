/**
 * The site's teacher–student pair. Names are PLACEHOLDERS until the owner picks a pair (plan, S0 gate).
 * MDX dialogue uses role tags (T: / S:), so renaming the characters never touches lesson files.
 */
export type Locale = 'zh-tw' | 'en';
export type CharacterId = 'teacher' | 'student';

export interface Character {
  id: CharacterId;
  /** speaker tags accepted in ```dialogue blocks (ASCII tags are case-insensitive) */
  tags: string[];
  name: Record<Locale, string>;
}

export const CHARACTERS: Record<CharacterId, Character> = {
  teacher: { id: 'teacher', tags: ['T', 'TEACHER', '老師'], name: { 'zh-tw': '老師', en: 'Teacher' } },
  student: { id: 'student', tags: ['S', 'STUDENT', '學生'], name: { 'zh-tw': '學生', en: 'Student' } },
};
