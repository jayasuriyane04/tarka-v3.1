import { useEffect, useRef, useState, type PointerEvent } from 'react';
import type { Lesson } from './types';
import './whiteboard.css';

export type BoardVisual =
  | { kind: 'counters'; groups: number[]; caption: string }
  | { kind: 'fraction'; numerator: number; denominator: number; caption: string }
  | { kind: 'number_line'; start: number; end: number; marks: number[]; caption: string }
  | { kind: 'rectangle'; length: number; width: number; caption: string };
export type BoardStep = { title: string; text: string; equation?: string | null; visual?: BoardVisual | null };
export type WhiteboardRequest = { lesson_id: string; segment: 'lesson' | 'hint' | 'feedback'; hint_level?: 1 | 2 | 3 };
export type WhiteboardResponse = { title: string; source: 'lesson' | 'nebius'; question_id: string; steps: BoardStep[] };
export type WhiteboardProps = { lesson: Lesson; intro: boolean; blocked: boolean; load: (request: WhiteboardRequest) => Promise<WhiteboardResponse> };

export function whiteboardChoices(lesson: Lesson) {
  const choices: { key: string; label: string; request: WhiteboardRequest }[] = [];
  if (lesson.subject !== 'maths') return choices;
  const add = (segment: WhiteboardRequest['segment'], label: string, hint_level?: 1 | 2 | 3) => choices.push({ key: `${segment}${hint_level ?? ''}`, label, request: { lesson_id: lesson.id, segment, ...(hint_level ? { hint_level } : {}) } });
  if (!lesson.state.completed) {
    if (lesson.question?.kind === 'practice') add('lesson', 'Teach the worked example');
    for (const hint of lesson.hints) if ([1, 2, 3].includes(hint.level)) add('hint', `Use hint ${hint.level}`, hint.level as 1 | 2 | 3);
  }
  if (lesson.last_feedback) add('feedback', 'Explain my checked answer');
  return choices;
}

export function BoardDiagram({ visual }: { visual: BoardVisual }) {
  let drawing;
  if (visual.kind === 'counters') drawing = <div className="wb-groups">{visual.groups.map((count, group) => <div className="wb-group" key={group}><span aria-hidden="true" className="wb-counter-grid">{Array.from({ length: count }, (_, index) => <i key={index}/>)}</span><strong>{count}</strong><span className="sr-only"> counters in group {group + 1}</span></div>)}</div>;
  else if (visual.kind === 'fraction') drawing = <div className="wb-fraction" aria-label={`${visual.numerator} of ${visual.denominator} equal parts shaded`}>{Array.from({ length: visual.denominator }, (_, index) => <span key={index} className={index < visual.numerator ? 'filled' : ''} aria-hidden="true"/>)}</div>;
  else if (visual.kind === 'rectangle') drawing = <svg className="wb-diagram" viewBox="0 0 520 210" role="img" aria-label={`Rectangle: length ${visual.length} centimetres, width ${visual.width} centimetres`}><rect x="100" y="35" width="300" height="125" rx="3" fill="#e4f4ee" stroke="#167364" strokeWidth="4"/><text x="250" y="24" textAnchor="middle">{visual.length} cm</text><text x="250" y="190" textAnchor="middle">{visual.length} cm</text><text x="55" y="100" textAnchor="middle">{visual.width} cm</text><text x="447" y="100" textAnchor="middle">{visual.width} cm</text><title>Schematic rectangle; side labels give the lengths.</title></svg>;
  else drawing = <svg className="wb-diagram" viewBox="0 0 520 115" role="img" aria-label={visual.caption}><line x1="35" y1="45" x2="485" y2="45" stroke="#167364" strokeWidth="3"/>{visual.marks.map((mark, index) => { const x = 35 + (mark - visual.start) / (visual.end - visual.start) * 450; return <g key={index}><line x1={x} y1="35" x2={x} y2="55" stroke="#167364" strokeWidth="3"/><circle cx={x} cy="45" r="5" fill="#167364"/><text x={x} y="85" textAnchor="middle">{mark}</text></g>; })}</svg>;
  return <figure className="wb-figure">{drawing}<figcaption>{visual.caption}</figcaption></figure>;
}

export type Point = { x: number; y: number };
export type Stroke = Point[];
const MAX_STROKES = 120;
const MAX_POINTS = 1000;
export function boundedPoint(x: number, y: number): Point {
  return { x: Math.min(800, Math.max(0, Number.isFinite(x) ? x : 0)), y: Math.min(300, Math.max(0, Number.isFinite(y) ? y : 0)) };
}
export function appendPoint(stroke: Stroke, point: Point): Stroke {
  return stroke.length < MAX_POINTS ? [...stroke, boundedPoint(point.x, point.y)] : stroke;
}
function squaredDistance(point: Point, a: Point, b: Point) {
  const dx = b.x - a.x, dy = b.y - a.y;
  const ratio = dx || dy ? Math.max(0, Math.min(1, ((point.x - a.x) * dx + (point.y - a.y) * dy) / (dx * dx + dy * dy))) : 0;
  return (point.x - a.x - ratio * dx) ** 2 + (point.y - a.y - ratio * dy) ** 2;
}
export function eraseAt(strokes: Stroke[], point: Point): Stroke[] {
  return strokes.filter((stroke) => !stroke.some((a, index) => squaredDistance(point, a, stroke[index + 1] ?? a) <= 18 ** 2));
}

export function DrawingPad() {
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [draft, setDraft] = useState<Stroke>([]);
  const [erasing, setErasing] = useState(false);
  const [note, setNote] = useState('');
  const active = useRef<{ id: number; points: Stroke } | null>(null);
  function position(event: PointerEvent<SVGSVGElement>) {
    const box = event.currentTarget.getBoundingClientRect();
    return boundedPoint((event.clientX - box.left) * 800 / Math.max(box.width, 1), (event.clientY - box.top) * 300 / Math.max(box.height, 1));
  }
  function start(event: PointerEvent<SVGSVGElement>) {
    if (active.current || event.button !== 0) return;
    event.preventDefault();
    const point = position(event);
    event.currentTarget.setPointerCapture(event.pointerId);
    active.current = { id: event.pointerId, points: [point] };
    if (erasing) setStrokes((old) => eraseAt(old, point));
    else if (strokes.length < MAX_STROKES) setDraft([point]);
  }
  function move(event: PointerEvent<SVGSVGElement>) {
    if (active.current?.id !== event.pointerId) return;
    const point = position(event);
    if (erasing) setStrokes((old) => eraseAt(old, point));
    else if (strokes.length < MAX_STROKES) { active.current.points = appendPoint(active.current.points, point); setDraft(active.current.points); }
  }
  function finish(event: PointerEvent<SVGSVGElement>) {
    if (active.current?.id !== event.pointerId) return;
    const stroke = active.current.points;
    active.current = null;
    if (!erasing && stroke.length) setStrokes((old) => old.length < MAX_STROKES ? [...old, stroke] : old);
    setDraft([]);
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
  }
  const paths = [...strokes, ...(draft.length ? [draft] : [])];
  return <div className="wb-scratch"><h3>Your thinking space</h3><p>Draw with a mouse, pen or touch, or type your thinking below. Your marks stay on this device and clear when this board closes. The tutor does not read or grade them.</p>
    <div className="wb-tools"><button type="button" className="button ghost" aria-pressed={!erasing} onClick={() => setErasing(false)}>Pen</button><button type="button" className="button ghost" aria-pressed={erasing} onClick={() => setErasing(true)}>Eraser</button><button type="button" className="button ghost" disabled={!strokes.length} onClick={() => setStrokes((old) => old.slice(0, -1))}>Undo stroke</button><button type="button" className="button ghost" disabled={!strokes.length && !note} onClick={() => { setStrokes([]); setDraft([]); active.current = null; setNote(''); }}>Clear my work</button></div>
    <svg viewBox="0 0 800 300" className={`wb-paper${erasing ? ' erasing' : ''}`} aria-label="Optional drawing space; use the text field below if you prefer typing" role="img" onPointerDown={start} onPointerMove={move} onPointerUp={finish} onPointerCancel={finish} onLostPointerCapture={finish}>{paths.map((stroke, index) => stroke.length === 1 ? <circle key={index} cx={stroke[0].x} cy={stroke[0].y} r="2.5" fill="#184e75"/> : <polyline key={index} points={stroke.map((point) => `${point.x},${point.y}`).join(' ')} fill="none" stroke="#184e75" strokeWidth="4" strokeLinejoin="round" strokeLinecap="round"/>)}</svg>
    {strokes.length >= MAX_STROKES && <p role="status">Your drawing space is full. Undo or clear some work to draw again.</p>}<label className="field"><span>Type my thinking instead</span><textarea value={note} maxLength={2000} rows={2} onChange={(event) => setNote(event.target.value)}/></label>
  </div>;
}

export function Whiteboard({ lesson, intro, blocked, load }: WhiteboardProps) {
  const [open, setOpen] = useState(false);
  const [selection, setSelection] = useState('');
  const [board, setBoard] = useState<WhiteboardResponse | null>(null);
  const [index, setIndex] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [openedContext, setOpenedContext] = useState('');
  const generation = useRef(0);
  const context = `${lesson.id}:${lesson.question?.id ?? 'complete'}:${intro}:${lesson.state.tries}:${lesson.state.answered}:${lesson.state.completed}:${lesson.hints.length}:${blocked}`;
  const choices = whiteboardChoices(lesson);
  const choice = choices.find((item) => item.key === selection) ?? choices[0];
  useEffect(() => { generation.current++; setOpen(false); setBoard(null); setBusy(false); setError(''); setIndex(0); setSelection(''); }, [context]);
  useEffect(() => () => { generation.current++; }, []);
  async function show() {
    if (!choice || blocked || busy) return;
    const version = ++generation.current;
    setBusy(true); setError(''); setBoard(null); setIndex(0); setOpen(true); setOpenedContext(context);
    try {
      const result = await load(choice.request);
      if (version !== generation.current) return;
      if (lesson.question && result.question_id !== lesson.question.id) throw new Error('The question changed. Open its board again.');
      if (!result.steps.length || result.steps.length > 6) throw new Error('This board could not be loaded. Please try again.');
      setBoard(result);
    } catch (err) { if (version === generation.current) setError(err instanceof Error ? err.message : 'This board could not be loaded. Please try again.'); }
    finally { if (version === generation.current) setBusy(false); }
  }
  function close() { generation.current++; setOpen(false); setBoard(null); setBusy(false); setError(''); }
  if (lesson.subject !== 'maths') return null;
  const step = board?.steps[index];
  return <section className="card whiteboard-card" aria-label="Optional maths whiteboard"><div className="wb-heading"><span className="pill teal">Optional whiteboard</span><span className="wb-pencil" aria-hidden="true">✎</span></div><h2>See the thinking</h2><p>Let the tutor unfold one step at a time. Make room for your own working too.</p>
    {!open || openedContext !== context || blocked ? <button type="button" className="button ghost" disabled={blocked} aria-expanded="false" onClick={() => { setOpen(true); setOpenedContext(context); }}>Open whiteboard</button> : <>
      <div className="wb-toolbar"><label className="field"><span>What shall we work through?</span><select value={choice?.key ?? ''} disabled={blocked || busy || !choices.length} onChange={(event) => { generation.current++; setSelection(event.target.value); setBoard(null); setError(''); setIndex(0); }}>{choices.length ? choices.map((item) => <option key={item.key} value={item.key}>{item.label}</option>) : <option value="">Your thinking space</option>}</select></label><button type="button" className="button primary" disabled={blocked || busy || !choice} onClick={() => { void show(); }}>{busy ? 'Getting the board…' : 'Teach on the board'}</button><button type="button" className="button ghost" onClick={close}>Close whiteboard</button></div>
      {lesson.question?.kind === 'transfer' && <p className="wb-note">This is your new challenge. Earlier worked examples stay closed. The tutor can show only a hint you have already opened or feedback from a checked answer.</p>}
      {!choices.length && <p className="wb-note">Try your own working below. To see a tutor step, first check an answer or open a hint.</p>}
      {error && <p role="alert" className="alert error">{error}</p>}
      {board && step && <div className="wb-teaching"><p className="hint-source">{board.source === 'nebius' ? 'NVIDIA-selected hint · approved lesson wording' : 'Authored tutor content · no live AI generation'}</p><h3>{board.title}</h3><div className="wb-step" aria-live="polite" aria-atomic="true"><span className="wb-step-count">Step {index + 1} of {board.steps.length}</span><h4>{step.title}</h4><p>{step.text}</p>{step.equation && <p className="wb-equation">{step.equation}</p>}{step.visual && <BoardDiagram visual={step.visual}/>}</div><div className="wb-controls"><button type="button" className="button ghost" disabled={index === 0 || blocked} onClick={() => setIndex((old) => old - 1)}>Previous step</button><button type="button" className="button primary" disabled={index === board.steps.length - 1 || blocked} onClick={() => setIndex((old) => old + 1)}>Next step</button><button type="button" className="button ghost" disabled={index === 0 || blocked} onClick={() => setIndex(0)}>Replay steps</button></div><p className="quiet">Tutor steps count as learning support. Your own drawing is not a hint.</p></div>}
      {!blocked && <DrawingPad key={`${context}:${selection}`}/>}
    </>}
  </section>;
}
