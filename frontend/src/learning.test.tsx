import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { LessonView, LessonVisual } from './App';
import type { Lesson } from './types';

function fixture(kind: 'practice' | 'transfer' = 'practice'): Lesson {
  return {
    id: 'reading-1', title: 'Look for clues', subject: 'reading', age_band: '6-8', skill: 'evidence', summary: 'Notice the clues.',
    explanation: 'Instructional explanation', worked_example: { prompt: 'Worked prompt', explanation: 'Worked solution' },
    passage: 'The original story belongs to practice.', visual: { kind: 'reading', focus: 'Read carefully.', caption: 'A reading guide.' },
    total_questions: 4, index: kind === 'transfer' ? 3 : 0,
    question: { id: 'q1', prompt: kind === 'transfer' ? 'A different story: the cat sat. Who sat?' : 'Who is in the original story?', options: ['A cat', 'A dog', 'A bird', 'A fish'], kind },
    state: { tries: 0, assistance_level: 0, answered: false, last_choice: null, completed: false, transfer_independent: false }, hints: [], last_feedback: null,
  };
}
function view(lesson: Lesson, intro = false) {
  const noop = () => undefined;
  return renderToStaticMarkup(<LessonView lesson={lesson} intro={intro} setIntro={noop} pending="" answer={noop} next={noop} hint={noop} home={noop} finalFeedback={null}/>);
}

describe('learning presentation boundaries', () => {
  it('keeps the new reading transfer separate from the practice story', () => {
    const html = view(fixture('transfer'));
    expect(html).toContain('A different story: the cat sat. Who sat?');
    expect(html).not.toContain('The original story belongs to practice.');
    expect(html).not.toContain('Look at the example');
    expect(html).toContain('Try a hint');
  });
  it('cannot reopen unrecorded example assistance during transfer via stale intro state', () => {
    const html = view(fixture('transfer'), true);
    expect(html).not.toContain('Instructional explanation');
    expect(html).not.toContain('Worked solution');
    expect(html).toContain('Check my thinking');
  });
  it('retains the story and example access for ordinary practice', () => {
    const html = view(fixture());
    expect(html).toContain('The original story belongs to practice.');
    expect(html).toContain('Look at the example');
  });
  it('keeps earlier progressive hints available after the third hint', () => {
    const lesson = fixture();
    lesson.hints = [1, 2, 3].map((level) => ({ level, source: 'lesson', message: `Written guidance ${level}` }));
    const html = view(lesson);
    for (const level of [1, 2, 3]) expect(html).toContain(`Written guidance ${level}`);
    expect(html).toContain('Your hints are all here');
  });
  it('renders authored or unexpected text safely without creating executable markup', () => {
    const lesson = fixture();
    lesson.question!.prompt = '<script>steal()</script>';
    lesson.hints = [{ level: 1, source: 'lesson', message: '<img src=x onerror=steal()>' }];
    const html = view(lesson);
    expect(html).toContain('&lt;script&gt;steal()&lt;/script&gt;');
    expect(html).not.toContain('<script>');
    expect(html).not.toContain('<img src=x');
  });
  it('does not label an assisted completion as independent transfer', () => {
    const lesson = fixture('transfer');
    lesson.state.completed = true;
    lesson.question = null;
    expect(view(lesson)).toContain('Supported practice recorded');
    expect(view(lesson)).not.toContain('Independent transfer recorded');
  });
  it('retains completed answer feedback when reopening without transient state', () => {
    const lesson = fixture('transfer');
    lesson.state.completed = true;
    lesson.question = null;
    lesson.last_feedback = { correct: true, message: 'Well thought through.', explanation: 'A cat is the one that sat.', evidence: 'The cat sat.' };
    const html = view(lesson);
    expect(html).toContain('Why that answer fits');
    expect(html).toContain('A cat is the one that sat.');
    expect(html).toContain('The cat sat.');
  });
});

describe('worked-example illustrations', () => {
  it('shows exactly the authored number of counters in each group', () => {
    const lesson = fixture();
    lesson.visual = { kind: 'counters', groups: [8, 5], caption: 'Eight and five counters.' };
    const html = renderToStaticMarkup(<LessonVisual lesson={lesson}/>);
    expect((html.match(/class="counter /g) ?? []).length).toBe(13);
    expect(html).toContain('aria-label="8 counters"');
    expect(html).toContain('aria-label="5 counters"');
    expect(html).toContain('A worked-example illustration');
  });
  it('shades the authored fraction of equal parts', () => {
    const lesson = fixture();
    lesson.visual = { kind: 'fraction', numerator: 3, denominator: 8 };
    const html = renderToStaticMarkup(<LessonVisual lesson={lesson}/>);
    expect((html.match(/class="shaded"/g) ?? []).length).toBe(3);
    expect(html).toContain('aria-label="3 out of 8 equal parts"');
  });
  it('renders the correct sequence for a positive-step number line', () => {
    const lesson = fixture();
    lesson.visual = { kind: 'number_line', start: -4, end: 4, step: 2 };
    const html = renderToStaticMarkup(<LessonVisual lesson={lesson}/>);
    for (const point of [-4, -2, 0, 2, 4]) expect(html).toContain(`<i></i>${point}</span>`);
  });
});
