import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { appendPoint, BoardDiagram, boundedPoint, DrawingPad, eraseAt, Whiteboard, whiteboardChoices, type Stroke } from './Whiteboard';
import type { Lesson } from './types';

const lesson: Lesson = { id: 'm68-01', title: 'Join groups', subject: 'maths', age_band: '6-8', skill: 'add', summary: 'Add.', explanation: 'Join.', worked_example: { prompt: '8 + 5', explanation: '13' }, visual: null, total_questions: 4, index: 0, question: { id: 'q1', prompt: '9 + 4', options: ['13', '14', '15', '16'], kind: 'practice' }, state: { tries: 0, assistance_level: 0, answered: false, last_choice: null, completed: false, transfer_independent: false }, hints: [], last_feedback: null };
const load = async () => ({ title: 'Approved board', source: 'lesson' as const, question_id: 'q1', steps: [{ title: 'Start', text: 'Think.' }] });

describe('whiteboard teaching boundaries', () => {
  it('is optional and closed before a deliberate action', () => {
    const html = renderToStaticMarkup(<Whiteboard lesson={lesson} intro blocked={false} load={load}/>);
    expect(html).toContain('Open whiteboard'); expect(html).toContain('aria-expanded="false"');
    expect(html).not.toContain('Teach on the board'); expect(html).not.toContain('8 + 5');
  });
  it('is disabled during a break and absent in reading', () => {
    expect(renderToStaticMarkup(<Whiteboard lesson={lesson} intro blocked load={load}/>)).toContain('disabled="" aria-expanded="false"');
    expect(renderToStaticMarkup(<Whiteboard lesson={{ ...lesson, subject: 'reading' }} intro blocked={false} load={load}/>)).toBe('');
  });
  it('offers worked examples only for practice, even with stale intro state', () => {
    expect(whiteboardChoices(lesson).map((item) => item.key)).toEqual(['lesson']);
    const transfer: Lesson = { ...lesson, question: { ...lesson.question!, kind: 'transfer' } };
    expect(whiteboardChoices(transfer)).toEqual([]);
    expect(renderToStaticMarkup(<Whiteboard lesson={transfer} intro blocked={false} load={load}/>)).not.toContain('8 + 5');
  });
  it('offers only delivered hint levels and checked feedback during transfer', () => {
    const transfer: Lesson = { ...lesson, question: { ...lesson.question!, kind: 'transfer' }, hints: [{ level: 1, source: 'nebius', message: 'Think.' }], last_feedback: { correct: false, message: 'Try again.' } };
    expect(whiteboardChoices(transfer).map((item) => item.key)).toEqual(['hint1', 'feedback']);
    expect(whiteboardChoices({ ...transfer, question: null, state: { ...transfer.state, completed: true } }).map((item) => item.key)).toEqual(['feedback']);
  });
});

describe('reference diagrams and private drawing', () => {
  it('shows the exact counter quantity and equal fraction subdivisions', () => {
    const counters = renderToStaticMarkup(<BoardDiagram visual={{ kind: 'counters', groups: [10, 3], caption: 'Thirteen.' }}/>);
    expect(counters.match(/<i>/g)).toHaveLength(13);
    const fraction = renderToStaticMarkup(<BoardDiagram visual={{ kind: 'fraction', numerator: 2, denominator: 4, caption: 'Half.' }}/>);
    expect(fraction.match(/class="filled"/g)).toHaveLength(2);
    expect(fraction).toContain('2 of 4 equal parts shaded');
  });
  it('maps duration marks proportionally and labels rectangle side units', () => {
    const line = renderToStaticMarkup(<BoardDiagram visual={{ kind: 'number_line', start: 0, end: 25, marks: [0, 15, 25], caption: 'Duration.' }}/>);
    expect(line).toContain('cx="35"'); expect(line).toContain('cx="305"'); expect(line).toContain('cx="485"');
    const rectangle = renderToStaticMarkup(<BoardDiagram visual={{ kind: 'rectangle', length: 6, width: 4, caption: 'Perimeter.' }}/>);
    expect(rectangle).toContain('length 6 centimetres, width 4 centimetres');
  });
  it('escapes caption text instead of interpreting markup', () => {
    const html = renderToStaticMarkup(<BoardDiagram visual={{ kind: 'counters', groups: [2], caption: '<script>steal()</script>' }}/>);
    expect(html).toContain('&lt;script&gt;'); expect(html).not.toContain('<script>');
  });
  it('offers an accessible typing alternative and states that work is not sent or graded', () => {
    const html = renderToStaticMarkup(<DrawingPad/>);
    expect(html).toContain('Type my thinking instead'); expect(html).toContain('The tutor does not read or grade them');
    expect(html).toContain('Undo stroke'); expect(html).toContain('Clear my work');
  });
  it('bounds drawing coordinates and total point allocation', () => {
    expect(boundedPoint(-2, 999)).toEqual({ x: 0, y: 300 });
    expect(boundedPoint(Number.NaN, Number.POSITIVE_INFINITY)).toEqual({ x: 0, y: 0 });
    let stroke: Stroke = [];
    for (let i = 0; i < 1200; i++) stroke = appendPoint(stroke, { x: i, y: i });
    expect(stroke).toHaveLength(1000);
    expect(stroke.every((point) => point.x <= 800 && point.y <= 300)).toBe(true);
  });
  it('erases an intersected line segment without removing distant strokes', () => {
    const first = [{ x: 0, y: 0 }, { x: 100, y: 0 }], second = [{ x: 0, y: 100 }, { x: 100, y: 100 }];
    expect(eraseAt([first, second], { x: 50, y: 0 })).toEqual([second]);
    expect(eraseAt([first, second], { x: 50, y: 50 })).toEqual([first, second]);
  });
});
