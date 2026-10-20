export type AgeBand = '6-8' | '9-11' | '12-15';
export type Subject = 'maths' | 'reading';
export type Profile = { nickname: string; age_band: AgeBand; ai_enabled: boolean; voice_enabled: boolean; session_minutes: 10 | 15 | 20 };
export type LessonSummary = { id: string; title: string; subject: Subject; age_band: AgeBand; skill: string; summary: string; completed: boolean; transfer_independent: boolean };
export type Progress = { completed_lessons: number; independent_transfers: number; practised_questions: number; total_lessons: number; by_subject: { subject: Subject; completed: number; independent: number; total: number }[] };
export type BreakState = { due: boolean; seconds_remaining: number; minutes: number; started: boolean; session_seconds_remaining: number };
export type AuthState = { authenticated: boolean; username: string | null; legacy_profile: boolean };
export type Bootstrap = { auth: AuthState; session: { id: string; csrf_token: string; setup_complete: boolean }; profile: Profile | null; lessons: LessonSummary[]; progress: Progress; break: BreakState; mode: { ai: 'lesson' | 'nebius_ready'; paid_enabled: boolean } };
export type Feedback = { correct: boolean; message: string; explanation?: string; evidence?: string };
export type Hint = { level: number; message: string; source: 'lesson' | 'nebius'; provider_notice?: string };
export type Lesson = {
  id: string; title: string; subject: Subject; age_band: AgeBand; skill: string; summary: string;
  explanation: string; worked_example: { prompt: string; explanation: string }; passage?: string;
  visual: { kind: string; groups?: number[]; numerator?: number; denominator?: number; start?: number; end?: number; step?: number; focus?: string; caption?: string } | null; total_questions: number; index: number;
  question: null | { id: string; prompt: string; options: string[]; kind: 'practice' | 'transfer' };
  state: { tries: number; assistance_level: number; answered: boolean; last_choice: number | null; completed: boolean; transfer_independent: boolean; voice_assisted?: boolean; narration_requests?: number; whiteboard_assisted?: boolean; whiteboard_requests?: number };
  hints: Hint[]; last_feedback: Feedback | null;
};
export type ParentOverview = { profile: Profile; progress: Progress; lessons: (LessonSummary & { attempts: number; hints_used: number; narration_requests: number; whiteboard_requests?: number })[]; usage: { reserved_usd: number; budget_usd: number; ai_requests: number; ai_available: boolean } };
export const subjectLabel = (subject: Subject) => subject === 'maths' ? 'Maths' : 'Reading';
export const ageLabel = (age: AgeBand) => age.replace('-', '–');
export function lessonEvidence(lesson: Pick<LessonSummary, 'completed' | 'transfer_independent'>): string {
  if (lesson.transfer_independent) return 'Independent transfer';
  if (lesson.completed) return 'Practised with support';
  return 'Ready to explore';
}

export type NarrationRequest = { lesson_id: string; segment: 'lesson' | 'question' | 'hint' | 'feedback'; hint_level?: 1 | 2 | 3 };
export type Narration = { text: string; label: string; source: 'lesson' | 'nebius'; question_id: string };
