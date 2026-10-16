import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { ProfileFields } from './App';
import { narrationChoices, VoicePanel } from './VoicePanel';
import type { Lesson, Narration } from './types';

const lesson: Lesson = {
  id: 'm68-01', title: 'Two groups', subject: 'maths', age_band: '6-8', skill: 'addition', summary: 'Count two groups.',
  explanation: 'Count both groups.', worked_example: { prompt: 'Two and three.', explanation: 'That makes five.' }, visual: null,
  total_questions: 4, index: 0, question: { id: 'q1', prompt: 'How many?', options: ['1', '2', '3', '4'], kind: 'practice' },
  state: { tries: 0, assistance_level: 0, answered: false, last_choice: null, completed: false, transfer_independent: false }, hints: [], last_feedback: null,
};
const prepare = async (): Promise<Narration> => ({ text: 'Approved words.', label: 'Question', source: 'lesson', question_id: 'q1' });

describe('voice presentation and lesson boundaries', () => {
  it('explains parent opt-in and retains text when narration is disabled', () => {
    const html = renderToStaticMarkup(<VoicePanel lesson={lesson} intro enabled={false} blocked={false} prepare={prepare}/>);
    expect(html).toContain('A grown-up can turn on read-aloud');
    expect(html).toContain('Device voice'); expect(html).toContain('No microphone');
    expect(html).not.toContain('>Play<');
  });
  it('requires deliberate playback and labels device speech separately from NVIDIA', () => {
    const html = renderToStaticMarkup(<VoicePanel lesson={lesson} intro enabled blocked={false} prepare={prepare}/>);
    expect(html).toContain('Nothing plays automatically');
    expect(html).toContain('Device speech is separate from NVIDIA hint selection');
    expect(html).toContain('disabled="">Play');
    expect(html).toContain('No local voice');
  });
  it('offers only delivered hints and only checked feedback', () => {
    expect(narrationChoices(lesson, false).map((item) => item.key)).toEqual(['question']);
    const checked: Lesson = { ...lesson, hints: [{ level: 1, source: 'lesson', message: 'Count once more.' }], last_feedback: { correct: false, message: 'Try again.' } };
    expect(narrationChoices(checked, false).map((item) => item.key)).toEqual(['question', 'hint1', 'feedback']);
  });
  it('cannot expose the worked example on a transfer even with stale intro state', () => {
    const transfer: Lesson = { ...lesson, question: { ...lesson.question!, kind: 'transfer' } };
    expect(narrationChoices(transfer, true).map((item) => item.key)).toEqual(['question']);
    const html = renderToStaticMarkup(<VoicePanel lesson={transfer} intro enabled blocked={false} prepare={prepare}/>);
    expect(html).toContain('counts as support');
    expect(html).not.toContain('Teach the idea');
  });
  it('offers only checked feedback after completion', () => {
    const completed: Lesson = { ...lesson, question: null, state: { ...lesson.state, completed: true }, last_feedback: { correct: true, message: 'That fits.' } };
    expect(narrationChoices(completed, true).map((item) => item.key)).toEqual(['feedback']);
  });
  it('keeps independent consent controls for voice and external hint selection', () => {
    const html = renderToStaticMarkup(<ProfileFields profile={{ nickname: 'Pebble', age_band: '6-8', ai_enabled: false, voice_enabled: false, session_minutes: 15 }} update={() => undefined}/>);
    expect((html.match(/type="checkbox"/g) ?? []).length).toBe(2);
    expect(html).not.toContain('checked=""');
    expect(html).toContain('Allow optional device read-aloud');
    expect(html).toContain('Allow optional NVIDIA-assisted hint selection');
    expect(html).toContain('recorded as support');
  });
});
