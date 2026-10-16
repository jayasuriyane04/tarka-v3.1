import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { api, ApiError, setCsrfToken, setParentToken } from './api';
import { Brand, Icon, LearningArt } from './art';
import { VoicePanel, type VoicePanelProps } from './VoicePanel';
import { ageLabel, lessonEvidence, subjectLabel, type AgeBand, type Bootstrap, type BreakState, type Feedback, type Lesson, type Narration, type NarrationRequest, type ParentOverview, type Profile, type Subject } from './types';

export function ProfileFields({ profile, update }: { profile: Profile; update: (value: Profile) => void }) {
  return <>
    <label className="field"><span>Learning nickname</span><input maxLength={20} value={profile.nickname} onChange={(event) => update({ ...profile, nickname: event.target.value })} placeholder="A nickname, not a full name" autoComplete="off"/><small>A made-up name is plenty. No school or birthday needed.</small></label>
    <fieldset className="field"><legend className="field-legend">Choose an age group</legend><div className="age-options">{(['6-8','9-11','12-15'] as AgeBand[]).map((age) => <button type="button" key={age} className={profile.age_band === age ? 'selected' : ''} aria-pressed={profile.age_band === age} onClick={() => update({ ...profile, age_band: age })}>{ageLabel(age)} years</button>)}</div></fieldset>
    <label className="field"><span>A gentle pause after</span><select value={profile.session_minutes} onChange={(event) => update({ ...profile, session_minutes: Number(event.target.value) as Profile['session_minutes'] })}><option value={10}>10 minutes</option><option value={15}>15 minutes</option><option value={20}>20 minutes</option></select><small>A one-minute screen break gives learning room to settle.</small></label>
    <label className="consent-option"><input type="checkbox" checked={profile.voice_enabled} onChange={(event) => update({ ...profile, voice_enabled: event.target.checked })}/><span><strong>Allow optional device read-aloud</strong><small>Choose a local English voice to read lesson explanations, questions, delivered hints and checked feedback. Nothing plays automatically, and there is no microphone. Reading a new transfer question aloud is recorded as support. This is off by default.</small></span></label>
    <label className="consent-option"><input type="checkbox" checked={profile.ai_enabled} onChange={(event) => update({ ...profile, ai_enabled: event.target.checked })}/><span><strong>Allow optional NVIDIA-assisted hint selection</strong><small>AI can choose from our written lesson hints using the age group, lesson and answer pattern. The nickname and PIN are not sent. This is off by default; lessons work without it.</small></span></label>
  </>;
}

function Onboarding({ onDone }: { onDone: (bootstrap: Bootstrap) => void }) {
  const [profile, setProfile] = useState<Profile>({ nickname: '', age_band: '6-8', ai_enabled: false, voice_enabled: false, session_minutes: 15 });
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [adult, setAdult] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  async function submit(event: FormEvent) {
    event.preventDefault(); setError('');
    if (!/^\d{6}$/.test(pin) || pin !== confirmPin) { setError('Choose a six-digit PIN and enter the same PIN in both boxes.'); return; }
    if (!adult) { setError('A parent or caregiver needs to complete this setup.'); return; }
    setPending(true);
    try { onDone(await api<Bootstrap>('/setup', { ...profile, nickname: profile.nickname.trim() || 'Learner', pin, adult_confirmed: true })); }
    catch (err) { setError((err as Error).message); } finally { setPending(false); }
  }
  return <div className="onboarding-shell"><section className="onboarding-intro"><p className="eyebrow">SMALL DISCOVERIES. ROOM TO GROW.</p><h1>A little wonder.<br/>A world to learn.</h1><p>A thoughtful space for maths and reading. Real ideas, helpful hints, and time to work things out.</p><LearningArt/><div className="onboarding-values"><span><Icon name="check"/>At their own pace</span><span><Icon name="check"/>No ads or rankings</span><span><Icon name="check"/>Parent controls</span></div></section><section className="card setup-card"><span className="pill purple setup-pill"><Icon name="shield" size={13}/>For a parent or caregiver</span><h2>Make a little learning space.</h2><p>One learner, one device, and a good place to begin.</p><form className="form-grid" onSubmit={(event) => void submit(event)}><ProfileFields profile={profile} update={setProfile}/><div className="field-row"><label className="field"><span>Parent PIN · 6 digits</span><input type="password" inputMode="numeric" pattern="[0-9]{6}" minLength={6} maxLength={6} value={pin} onChange={(event) => setPin(event.target.value.replace(/\D/g, ''))} autoComplete="new-password" required/></label><label className="field"><span>Confirm parent PIN</span><input type="password" inputMode="numeric" pattern="[0-9]{6}" minLength={6} maxLength={6} value={confirmPin} onChange={(event) => setConfirmPin(event.target.value.replace(/\D/g, ''))} autoComplete="new-password" required/></label></div><label className="consent-option"><input type="checkbox" checked={adult} onChange={(event) => setAdult(event.target.checked)} required/><span>I am an adult parent or caregiver setting this up. I understand this prototype is a learning aid, not a substitute for adult guidance.</span></label>{error && <div className="alert error" role="alert">{error}</div>}<button className="button primary" disabled={pending}>{pending ? 'Making your space…' : 'Let’s begin'}<Icon name="arrow" size={17}/></button></form><div className="setup-note"><Icon name="lock" size={14}/><p>Keep the PIN somewhere you can find it. This household PIN is a convenience lock, not verified parental identity. This browser session lasts up to 30 days. There is no recovery after its cookie expires or is cleared; export your record before then.</p></div></section></div>;
}

function Dashboard({ bootstrap, openLesson, takeBreak }: { bootstrap: Bootstrap; openLesson: (id: string) => void; takeBreak: () => void }) {
  const [subject, setSubject] = useState<'all' | Subject>('all');
  const profile = bootstrap.profile!;
  const next = bootstrap.lessons.find((item) => !item.completed) ?? bootstrap.lessons[0];
  const filtered = bootstrap.lessons.filter((item) => subject === 'all' || item.subject === subject);
  return <>
    <div className="page-heading"><div><p className="eyebrow">YOUR LITTLE CORNER OF CURIOSITY</p><h1>Hello, {profile.nickname}.</h1><p>What shall we discover today?</p></div><span className="pill purple">Ages {ageLabel(profile.age_band)}</span></div>
    <section className="welcome-hero"><div className="hero-copy"><p className="eyebrow">A GOOD QUESTION IS A GREAT START</p><h2>{profile.age_band === '12-15' ? <>Think deeper.<br/>See things differently.</> : <>Big ideas start<br/>with little discoveries.</>}</h2><p>{profile.age_band === '6-8' ? 'Play with numbers. Step into a story. Take your time and see what you can work out.' : 'Explore a new idea, try it out, then see where else it takes you. There is no race to the finish.'}</p>{next && <button className="button primary" onClick={() => openLesson(next.id)}>Explore a lesson<Icon name="arrow" size={16}/></button>}</div><div className="hero-art"><LearningArt/></div></section>
    <div className="section-heading"><h2>A world to explore</h2><p>{bootstrap.lessons.length} short lessons, at your pace</p></div>
    <div className="subject-tabs" aria-label="Filter lessons">{(['all','maths','reading'] as const).map((item) => <button key={item} className={subject === item ? 'selected' : ''} aria-pressed={subject === item} onClick={() => setSubject(item)}>{item !== 'all' && <Icon name={item === 'maths' ? 'maths' : 'book'} size={16}/>} {item === 'all' ? 'All discoveries' : subjectLabel(item)}</button>)}</div>
    <div className="lesson-grid">{filtered.map((item) => <button key={item.id} className={`card lesson-card ${item.subject}`} onClick={() => openLesson(item.id)}><div className="lesson-art"><span className="pill">{subjectLabel(item.subject)}</span><LearningArt kind={item.subject} compact/></div><div className="lesson-card-body"><h3>{item.title}</h3><p>{item.summary}</p><div className="lesson-card-footer"><span>{item.completed ? <><Icon name="check" size={13}/>{item.transfer_independent ? 'New idea tried independently' : 'Explored with practice'}</> : 'Learn · practise · try something new'}</span><Icon name="arrow" size={17}/></div></div></button>)}</div>
    <div className="gentle-note"><Icon name="leaf" size={23}/><p><strong>A good pause belongs in a good learning day.</strong> Your place will be here when you come back.</p><button className="text-button" onClick={takeBreak}>Take a break<Icon name="arrow" size={14}/></button></div>
  </>;
}

export function LessonVisual({ lesson }: { lesson: Lesson }) {
  const [revealed, setRevealed] = useState(false);
  const visual = lesson.visual;
  if (!visual) return null;
  let picture: ReactNode = null;
  if (visual.kind === 'counters' && visual.groups) {
    picture = <div className="counter-groups">{visual.groups.map((count, index) => <div className="counter-group" key={index} aria-label={`${count} counters`}><div>{Array.from({ length: Math.min(30, Math.max(0, count)) }, (_, item) => <span className={`counter ${index % 2 ? 'lavender' : ''} ${revealed ? 'revealed' : ''}`} key={item} style={{ animationDelay: `${item * 35}ms` }}/>)}</div><span>{revealed ? count : '?'}</span></div>)}</div>;
  } else if (visual.kind === 'fraction' && visual.denominator && visual.denominator <= 16) {
    picture = <div className="fraction-picture"><div className="fraction-bar" aria-label={`${visual.numerator} out of ${visual.denominator} equal parts`}>{Array.from({ length: visual.denominator }, (_, index) => <span key={index} className={index < (visual.numerator ?? 0) ? 'shaded' : ''}/>)}</div>{revealed && <span className="fraction-label">{visual.numerator} / {visual.denominator}</span>}</div>;
  } else if (visual.kind === 'number_line' && visual.start !== undefined && visual.end !== undefined && visual.step && visual.step > 0) {
    const points = Array.from({ length: Math.min(20, Math.floor((visual.end - visual.start) / visual.step) + 1) }, (_, index) => visual.start! + index * visual.step!);
    picture = <div className="number-line">{points.map((point) => <span key={point}><i/>{point}</span>)}</div>;
  } else if (visual.kind === 'reading') picture = <div className="reading-focus"><Icon name="book" size={21}/><span>{visual.focus}</span></div>;
  if (!picture) return null;
  return <figure className="lesson-figure"><div className="visual-label">A worked-example illustration</div>{picture}<figcaption>{visual.caption}</figcaption>{['counters','fraction'].includes(visual.kind) && <button className="text-button" onClick={() => setRevealed(!revealed)}>{revealed ? 'Hide the labels' : 'Show the labels'}<Icon name="arrow" size={14}/></button>}</figure>;
}

export function LessonView({ lesson, intro, setIntro, pending, answer, next, hint, home, finalFeedback, voice }: { voice?: Omit<VoicePanelProps, 'lesson' | 'intro'>; lesson: Lesson; intro: boolean; setIntro: (value: boolean) => void; pending: string; answer: (choice: number) => void; next: () => void; hint: () => void; home: () => void; finalFeedback: Feedback | null }) {
  const [choice, setChoice] = useState<number | null>(lesson.state.last_choice);
  useEffect(() => { setChoice(lesson.state.last_choice); }, [lesson.question?.id, lesson.state.last_choice]);
  const question = lesson.question;
  const latestHint = lesson.hints.at(-1);
  finalFeedback = finalFeedback ?? lesson.last_feedback;
  const isTransfer = question?.kind === 'transfer';
  // A transfer attempt must never expose unrecorded worked-example assistance.
  intro = intro && !isTransfer;
  if (lesson.state.completed) return <><div className="lesson-heading"><button className="text-button" onClick={home}><Icon name="back" size={15}/>All discoveries</button></div><section className="card completion-card"><div className="completion-icon"><Icon name="leaf" size={35}/></div><p className="eyebrow">AN IDEA TO TAKE WITH YOU</p><h1>You explored something new.</h1><p>{lesson.state.transfer_independent ? 'You used the idea on a new question without hints or read-aloud support. That is a useful sign of understanding.' : 'You worked through the idea with practice or a little help. Every thoughtful attempt gives you something to build on.'}</p>{finalFeedback?.explanation && <div className="completion-explanation"><strong>Why that answer fits</strong><p>{finalFeedback.explanation}</p>{finalFeedback.evidence && <p>{finalFeedback.evidence}</p>}</div>}<div><span className={`pill ${lesson.state.transfer_independent ? 'teal' : 'purple'}`}>{lesson.state.transfer_independent ? 'Independent transfer recorded' : 'Supported practice recorded'}</span></div><button className="button primary" onClick={home}>Back to discoveries<Icon name="arrow" size={17}/></button><p className="quiet">One lesson is a step in learning. It does not prove mastery of a whole subject.</p></section>{voice && <div className="completion-voice"><VoicePanel {...voice} lesson={lesson} intro={false}/></div>}</>;
  return <><div className="lesson-heading"><button className="text-button" disabled={!!pending} onClick={home}><Icon name="back" size={15}/>All discoveries</button><span className={`pill ${lesson.subject === 'maths' ? 'teal' : 'gold'}`}>{subjectLabel(lesson.subject)} · Ages {ageLabel(lesson.age_band)}</span></div><div className="lesson-layout"><section className="card lesson-main"><div className="lesson-topline"><span className="eyebrow">ONE IDEA, A FEW SMALL STEPS</span><span>{intro ? 'Room to understand' : `Question ${lesson.index + 1} of ${lesson.total_questions}`}</span></div><div className="lesson-stages"><span className={intro ? 'current' : ''}><i className="stage-dot">1</i>Explore</span><span className="stage-line"/><span className={!intro && !isTransfer ? 'current' : ''}><i className="stage-dot">2</i>Practise</span><span className="stage-line"/><span className={!intro && isTransfer ? 'current' : ''}><i className="stage-dot">3</i>Try a new idea</span></div><div className="lesson-content"><h1>{lesson.title}</h1>{intro ? <><p className="lesson-intro">{lesson.explanation}</p>{lesson.passage && <div className="reading-passage">{lesson.passage}</div>}<LessonVisual key={lesson.id} lesson={lesson}/><div className="learning-example"><span className="eyebrow">LET’S LOOK TOGETHER</span><strong>{lesson.worked_example.prompt}</strong><p>{lesson.worked_example.explanation}</p></div><div className="lesson-actions"><p className="quiet">You can come back to this example whenever you need.</p><button className="button primary" onClick={() => setIntro(false)}>Let’s try it<Icon name="arrow" size={16}/></button></div></> : question && <>{lesson.passage && !isTransfer && <details className="passage-review" open><summary>Read the story</summary><div className="reading-passage">{lesson.passage}</div></details>}<div className="question-block"><p className="eyebrow">{isTransfer ? 'A FRESH QUESTION · THE SAME IDEA' : 'HAVE A GO. TAKE YOUR TIME.'}</p><h2>{question.prompt}</h2><fieldset className="question-options"><legend className="sr-only">Choose an answer</legend>{question.options.map((option, index) => <label key={`${question.id}-${index}`} className={`${choice === index ? 'selected' : ''} ${lesson.state.answered && lesson.state.last_choice === index ? 'correct' : ''}`}><input type="radio" name={question.id} checked={choice === index} disabled={!!pending || lesson.state.answered} onChange={() => setChoice(index)}/><span className="option-marker">{String.fromCharCode(65 + index)}</span><span>{option}</span>{lesson.state.answered && lesson.state.last_choice === index && <Icon name="check" size={18}/>}</label>)}</fieldset>{lesson.last_feedback && <div className={`feedback ${lesson.last_feedback.correct ? '' : 'retry'}`} role="status"><Icon name={lesson.last_feedback.correct ? 'check' : 'leaf'} size={20}/><div><strong>{lesson.last_feedback.message}</strong>{lesson.last_feedback.explanation && <p>{lesson.last_feedback.explanation}</p>}{lesson.last_feedback.evidence && <p>{lesson.last_feedback.evidence}</p>}</div></div>}<div className="lesson-actions">{!isTransfer && <button className="text-button" disabled={!!pending} onClick={() => setIntro(true)}><Icon name="book" size={15}/>Look at the example</button>}{lesson.state.answered ? <button className="button primary" disabled={!!pending} onClick={next}>{pending === 'continue' ? 'Opening…' : 'Next small step'}<Icon name="arrow" size={16}/></button> : <button className="button primary" disabled={choice === null || !!pending} onClick={() => choice !== null && answer(choice)}>{pending === 'answer' ? 'Checking…' : 'Check my thinking'}<Icon name="check" size={16}/></button>}</div></div></>}</div></section><aside className="lesson-aside">{voice && <VoicePanel {...voice} lesson={lesson} intro={intro}/>}<section className="card hint-card"><span className="hint-icon"><Icon name="bulb" size={22}/></span><h2>A little help to think.</h2><p>{latestHint?.message ?? 'Sometimes a small hint helps an idea click. You can ask for one when you are ready.'}</p>{!intro && <button className="button" disabled={!!pending || lesson.hints.length >= 3 || lesson.state.answered} onClick={hint}><Icon name="bulb" size={16}/>{pending === 'hint' ? 'Finding a helpful hint…' : lesson.hints.length >= 3 ? 'Your hints are all here' : 'Try a hint'}</button>}<span className="hint-source">{latestHint?.source === 'nebius' ? 'NVIDIA-selected lesson guide' : 'Lesson guide'}{latestHint ? ` · hint ${latestHint.level} of 3` : ''}</span>{latestHint?.provider_notice && <p className="quiet">We’re using a written lesson guide for this hint.</p>}{lesson.hints.length > 1 && <details className="hint-history"><summary>See your earlier hints</summary><ol>{lesson.hints.slice(0, -1).map((item) => <li key={item.level}>{item.message}</li>)}</ol></details>}{isTransfer && <p className="quiet">Try the new question first, or ask for a hint. We’ll remember when a try had a little help.</p>}</section><section className="card lesson-tip"><Icon name="leaf" size={26}/><h3>Slow thinking is good thinking.</h3><p>You can pause, read again, or talk the idea through with someone you trust.</p></section></aside></div></>;
}

function ParentGate({ onUnlock, onBack, onBusy }: { onUnlock: (value: ParentOverview, seconds: number) => void; onBack: () => void; onBusy: (value: boolean) => void }) {
  const [pin, setPin] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  async function unlock(event: FormEvent) {
    event.preventDefault(); setPending(true); onBusy(true); setError('');
    try { const result = await api<{ parent_token: string; expires_in: number }>('/parent/unlock', { pin }); setParentToken(result.parent_token); const overview = await api<ParentOverview>('/parent/overview'); setPin(''); onUnlock(overview, result.expires_in); }
    catch (err) { setParentToken(''); setError((err as Error).message); } finally { setPending(false); onBusy(false); }
  }
  return <section className="card pin-panel"><span className="large-icon"><Icon name="lock" size={26}/></span><h1>A space for grown-ups.</h1><p>Enter your parent PIN to see learning progress, change settings or manage the profile.</p><form className="form-grid" onSubmit={(event) => void unlock(event)}><label className="field"><span>Your six-digit PIN</span><input className="pin-input" type="password" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} minLength={6} value={pin} onChange={(event) => setPin(event.target.value.replace(/\D/g, ''))} autoComplete="current-password" required autoFocus/></label>{error && <div className="alert error" role="alert">{error}</div>}<button className="button primary" disabled={pending || pin.length !== 6}>{pending ? 'Opening…' : 'Open parent space'}<Icon name="arrow" size={16}/></button></form><button className="text-button" disabled={pending} onClick={onBack}><Icon name="back" size={14}/>Back to learning</button><p className="quiet pin-reminder">The PIN protects settings on this household session. It does not verify parental identity.</p></section>;
}

function Modal({ children, label }: { children: ReactNode; label: string }) {
  const container = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const prior = document.activeElement as HTMLElement | null;
    const first = container.current?.querySelector<HTMLElement>('button:not(:disabled),input'); first?.focus();
    const previousOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = previousOverflow; prior?.focus(); };
  }, []);
  return <div className="modal-backdrop"><div className="modal-card" role="dialog" aria-modal="true" aria-label={label} ref={container} onKeyDown={(event) => {
    if (event.key !== 'Tab') return;
    const items = Array.from(container.current?.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled),select') ?? []);
    if (!items.length) return;
    if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items.at(-1)?.focus(); }
    if (!event.shiftKey && document.activeElement === items.at(-1)) { event.preventDefault(); items[0].focus(); }
  }}>{children}</div></div>;
}

function BreakDialog({ state, pending, start, finish, parent, error }: { state: BreakState; pending: string; start: () => void; finish: () => void; parent: () => void; error: string }) {
  const [remaining, setRemaining] = useState(state.seconds_remaining);
  useEffect(() => {
    const until = Date.now() + state.seconds_remaining * 1000;
    setRemaining(state.seconds_remaining);
    const interval = window.setInterval(() => setRemaining(Math.max(0, Math.ceil((until - Date.now()) / 1000))), 500);
    return () => window.clearInterval(interval);
  }, [state.seconds_remaining, state.started]);
  return <Modal label="Time for a small pause"><div className="break-art"><Icon name="leaf" size={37}/></div><p className="eyebrow">YOUR PLACE IS SAVED</p><h2>Let’s take a little pause.</h2><p>Stretch your hands. Look at something far away. Get a sip of water if you like.</p>{state.started ? <><div className="break-clock" aria-live="off">{remaining > 0 ? `${remaining}s` : 'Ready when you are'}</div><p className="quiet">There’s no rush to return. Your learning will wait.</p><button className="button primary full-width" disabled={!!pending || remaining > 0} onClick={finish}>{pending === 'break' ? 'Checking your pause…' : 'I’m ready to return'}<Icon name="arrow" size={16}/></button></> : <button className="button primary full-width" disabled={!!pending} onClick={start}>{pending === 'break' ? 'Saving your pause…' : 'Start a quiet minute'}<Icon name="leaf" size={16}/></button>}{error && <div className="alert error" role="alert">{error}</div>}<button className="text-button break-parent" disabled={!!pending} onClick={parent}><Icon name="shield" size={14}/>Parent space</button></Modal>;
}

function ParentView({ overview, save, onExport, onDelete, onLock, pending, message }: { overview: ParentOverview; save: (profile: Profile) => void; onExport: () => void; onDelete: () => void; onLock: () => void; pending: string; message: string }) {
  const [tab, setTab] = useState<'progress' | 'settings'>('progress');
  const [profile, setProfile] = useState(overview.profile);
  const [deleting, setDeleting] = useState(false);
  const [confirmation, setConfirmation] = useState('');
  useEffect(() => setProfile(overview.profile), [overview.profile]);
  return <><div className="page-heading"><div className="parent-intro"><span className="large-icon"><Icon name="shield" size={24}/></span><div><p className="eyebrow">A THOUGHTFUL VIEW OF LEARNING</p><h1>Parent space</h1></div></div><button className="button ghost" disabled={!!pending} onClick={onLock}><Icon name="lock" size={15}/>Lock & return</button></div><div className="parent-nav"><button className={tab === 'progress' ? 'active' : ''} onClick={() => setTab('progress')}><Icon name="leaf" size={16}/>Learning picture</button><button className={tab === 'settings' ? 'active' : ''} onClick={() => setTab('settings')}><Icon name="settings" size={16}/>Settings & privacy</button></div>{message && <div className="parent-success" role="status">{message}</div>}{tab === 'progress' ? <><div className="stats-grid"><div className="card stat-card"><span className="stat-number">{overview.progress.completed_lessons}</span><h3>Lessons explored</h3><p>Includes practice with hints or retries.</p></div><div className="card stat-card"><span className="stat-number">{overview.progress.independent_transfers}</span><h3>Independent transfer answers</h3><p>A new question, correct first time, without hints or read-aloud support.</p></div><div className="card stat-card"><span className="stat-number">{overview.progress.practised_questions}</span><h3>Questions practised</h3><p>Thoughtful attempts matter, too.</p></div></div><div className="parent-columns"><section className="card parent-section"><h2>{overview.profile.nickname}’s learning picture</h2><p>A small record of practice, not a grade or a diagnosis.</p><div className="table-scroll"><table className="progress-table"><thead><tr><th scope="col">LESSON</th><th scope="col">TRIES / HINTS / READ-ALOUD</th><th scope="col">EVIDENCE</th></tr></thead><tbody>{overview.lessons.map((item) => <tr key={item.id}><td>{item.title}<small>{subjectLabel(item.subject)}</small></td><td>{item.attempts} / {item.hints_used} / {item.narration_requests ?? 0}</td><td>{lessonEvidence(item)}</td></tr>)}</tbody></table></div><p className="quiet">Independent transfer describes one observed answer. It does not establish broad mastery or prove that no outside help was used.</p></section><section className="card parent-section"><h2>Make room for a conversation.</h2><p>Ask “What did you notice?” or “Can you show me another way?” A calm conversation can reveal more than a score.</p><div className="provider-state"><span className="status-dot"/>{overview.profile.ai_enabled && overview.usage.ai_available ? 'NVIDIA hint selection is available' : overview.profile.ai_enabled ? 'AI consent saved · service not configured' : 'Written lesson guides · AI consent off'}</div><p className="quiet">{overview.usage.ai_requests} AI selection requests recorded. Children see only authored lesson hints, including when a model helps choose one.</p></section></div></> : <div className="parent-columns"><section className="card parent-section"><h2>Keep it right for your learner.</h2><p>Changing the age group shows a different collection. Existing records remain available in the data export.</p><form className="settings-form" onSubmit={(event) => { event.preventDefault(); save({ ...profile, nickname: profile.nickname.trim() || 'Learner' }); }}><ProfileFields profile={profile} update={setProfile}/><button className="button primary" disabled={!!pending}>{pending === 'settings' ? 'Saving…' : 'Save settings'}<Icon name="check" size={16}/></button></form></section><div><section className="card parent-section"><h2>Your data, in your hands.</h2><p>The profile and lesson attempts are stored on this app’s server and associated with this browser session. There is no public profile or open chat. This browser session lasts up to 30 days. If the cookie expires or is cleared, there is no recovery: export your record before then.</p><div className="setting-block"><h3>Download the learning record</h3><p>Export the nickname, settings, answers, hints and read-aloud requests as a JSON file.</p><button className="button ghost" disabled={!!pending} onClick={onExport}><Icon name="download" size={15}/>{pending === 'export' ? 'Preparing…' : 'Export data'}</button></div><div className="setting-block"><h3>Optional NVIDIA / Nebius service</h3><p>Consent: {overview.profile.ai_enabled ? 'on' : 'off'}. Availability: {overview.usage.ai_available ? 'configured' : 'not configured'}. The model chooses a hint identifier; its free-form output is never shown to a child.</p><p className="quiet">Configured project spending ceiling: ${overview.usage.budget_usd.toFixed(2)}. Reserved provider cost: ${overview.usage.reserved_usd.toFixed(4)}. Availability does not confirm a successful live model call.</p></div></section><section className="card parent-section destructive-section"><h2>Delete this learning space</h2><p>Remove this profile, answers and hints from the app. This cannot be undone. Export anything you want to keep first.</p><button className="button ghost" disabled={!!pending} onClick={() => setDeleting(true)}>Delete profile and progress</button></section></div></div>}{deleting && <Modal label="Delete profile and progress"><h2>Delete this learning space?</h2><p>This removes {overview.profile.nickname}’s profile and learning history from the app. It cannot be undone.</p><label className="field"><span>Type DELETE to confirm</span><input value={confirmation} onChange={(event) => setConfirmation(event.target.value)} autoComplete="off"/></label><div className="modal-actions"><button className="button ghost" disabled={!!pending} onClick={() => { setDeleting(false); setConfirmation(''); }}>Keep profile</button><button className="button danger" disabled={confirmation !== 'DELETE' || !!pending} onClick={onDelete}>{pending === 'delete' ? 'Deleting…' : 'Delete profile'}</button></div></Modal>}</>;
}

export default function App() {
  const [bootstrap, setBootstrap] = useState<Bootstrap | null>(null);
  const [bootError, setBootError] = useState('');
  const [page, setPage] = useState<'home' | 'lesson' | 'parent-gate' | 'parent'>('home');
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [intro, setIntro] = useState(true);
  const [pending, setPending] = useState('');
  const [error, setError] = useState('');
  const [parentOverview, setParentOverview] = useState<ParentOverview | null>(null);
  const [parentUntil, setParentUntil] = useState(0);
  const [parentMessage, setParentMessage] = useState('');
  const [finalFeedback, setFinalFeedback] = useState<Feedback | null>(null);
  const requestInFlight = useRef(false);
  const refreshGeneration = useRef(0);
  function acceptBootstrap(value: Bootstrap) { setCsrfToken(value.session.csrf_token); setBootstrap(value); }
  async function refresh() {
    const generation = ++refreshGeneration.current;
    const value = await api<Bootstrap>('/bootstrap');
    if (generation === refreshGeneration.current) acceptBootstrap(value);
    return value;
  }
  async function load() { setBootError(''); try { await refresh(); } catch (err) { setBootError((err as Error).message); } }
  useEffect(() => { void load(); }, []);
  useEffect(() => {
    if (!bootstrap?.session.setup_complete) return;
    const timer = window.setInterval(() => { if (!requestInFlight.current) void refresh().catch(() => undefined); }, 15000);
    return () => window.clearInterval(timer);
  }, [bootstrap?.session.id, bootstrap?.session.setup_complete]);
  useEffect(() => {
    if (!parentUntil) return;
    const timer = window.setTimeout(() => { setParentToken(''); setParentOverview(null); setParentUntil(0); setPage((current) => current === 'parent' ? 'parent-gate' : current); setError('Your parent space has locked. Enter your PIN to reopen it.'); }, Math.max(0, parentUntil - Date.now()));
    return () => window.clearTimeout(timer);
  }, [parentUntil]);
  function clearParentView() { setParentToken(''); setParentUntil(0); setParentOverview(null); }
  async function home() {
    if (requestInFlight.current) return;
    const leave = () => { clearParentView(); setPage('home'); setError(''); setParentMessage(''); };
    if (parentUntil) await action('lock', async () => { await api('/parent/lock', {}); leave(); });
    else leave();
  }
  function openParent() { if (requestInFlight.current) return; setParentToken(''); setParentOverview(null); setParentUntil(0); setError(''); setPage('parent-gate'); }
  async function action(name: string, operation: () => Promise<void>) {
    if (requestInFlight.current) return;
    requestInFlight.current = true;
    // A bootstrap begun before this write must not restore stale progress or CSRF state.
    refreshGeneration.current += 1;
    setPending(name); setError(''); setParentMessage('');
    try { await operation(); }
    catch (err) {
      if (err instanceof ApiError && err.status === 423) { await refresh().catch(() => undefined); }
      else if (err instanceof ApiError && err.status === 403 && page === 'parent') { setParentToken(''); setParentUntil(0); setParentOverview(null); setPage('parent-gate'); }
      setError((err as Error).message);
    } finally { requestInFlight.current = false; setPending(''); }
  }
  function applyLesson(value: Lesson) { setLesson(value); setFinalFeedback(null); }
  async function openLesson(id: string) {
    await action('lesson', async () => { const value = await api<Lesson>(`/lessons/${encodeURIComponent(id)}`); applyLesson(value); setIntro(value.question?.kind !== 'transfer' && value.index === 0 && value.state.tries === 0 && value.hints.length === 0); setPage('lesson'); await refresh(); });
  }
  async function answer(choice: number) {
    if (!lesson) return;
    await action('answer', async () => { const result = await api<Feedback & { can_continue: boolean; lesson: Lesson; progress: Bootstrap['progress'] }>('/answer', { lesson_id: lesson.id, choice }); applyLesson(result.lesson); setFinalFeedback(result); setBootstrap((previous) => previous ? { ...previous, progress: result.progress } : previous); if (result.lesson.state.completed) await refresh(); });
  }
  async function next() { if (lesson) await action('continue', async () => { applyLesson(await api<Lesson>('/continue', { lesson_id: lesson.id })); setIntro(false); }); }
  async function hint() { if (lesson) await action('hint', async () => { const value = await api<{ lesson: Lesson }>('/hints', { lesson_id: lesson.id }); applyLesson(value.lesson); }); }
  async function prepareNarration(request: NarrationRequest): Promise<Narration> {
    if (requestInFlight.current) throw new Error('Finish the current step, then try read-aloud again.');
    requestInFlight.current = true; refreshGeneration.current += 1; setPending('narration');
    try {
      const narration = await api<Narration>('/narration', request);
      // Update server-recorded support before allowing the learner to submit another answer.
      const updated = await api<Lesson>(`/lessons/${encodeURIComponent(request.lesson_id)}`);
      setLesson(updated);
      return narration;
    } catch (err) {
      if (err instanceof ApiError && err.status === 423) await refresh().catch(() => undefined);
      throw err;
    } finally { requestInFlight.current = false; setPending(''); }
  }
  async function breakAction(endpoint: 'start' | 'finish') { await action('break', async () => { const value = await api<BreakState>(`/break/${endpoint}`, {}); setBootstrap((previous) => previous ? { ...previous, break: value } : previous); if (endpoint === 'finish') await refresh(); }); }
  async function saveSettings(profile: Profile) { await action('settings', async () => { acceptBootstrap(await api<Bootstrap>('/parent/settings', profile)); setParentOverview(await api<ParentOverview>('/parent/overview')); setLesson(null); setParentMessage('Settings saved. The learning space is ready.'); }); }
  async function exportData() {
    await action('export', async () => { const value = await api<unknown>('/parent/export'); const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' })); const link = document.createElement('a'); link.href = url; link.download = 'tarka-family-learning-record.json'; document.body.append(link); link.click(); link.remove(); window.setTimeout(() => URL.revokeObjectURL(url), 1000); setParentMessage('Your data export is ready in your downloads.'); });
  }
  async function deleteProfile() {
    await action('delete', async () => { await api('/parent/delete-profile', { confirm: true }); setParentToken(''); setParentOverview(null); setParentUntil(0); setLesson(null); setPage('home'); await refresh(); });
  }
  if (!bootstrap) return <div className="boot-screen"><Brand/><div className="boot-content">{bootError ? <><h1>Let’s get connected.</h1><p>{bootError}</p><button className="button primary" onClick={() => void load()}>Try again<Icon name="arrow" size={17}/></button></> : <><span className="spinner"/><p>Opening a little space to learn…</p></>}</div><p className="boot-tagline">A little wonder. A world to learn.</p></div>;
  const profile = bootstrap.profile;
  const parentPage = page === 'parent' || page === 'parent-gate';
  return <div className={`family-app ${profile ? `age-${profile.age_band}` : ''}`}><header className="site-header"><button className="brand-button" aria-label="Tarka home" disabled={!!pending} onClick={() => void home()}><Brand/></button>{profile && <nav className="header-nav" aria-label="Main navigation"><button className={!parentPage ? 'active' : ''} disabled={!!pending} onClick={() => void home()}><Icon name="home" size={16}/>My discoveries</button></nav>}<div className="header-actions">{profile && <><button className="parent-link" disabled={!!pending} onClick={() => parentPage ? void home() : openParent()}><Icon name={parentPage ? 'back' : 'shield'} size={15}/>{parentPage ? 'Back to learning' : 'Parent space'}</button><div className="header-child"><span className="avatar">{profile.nickname.slice(0,1).toUpperCase()}</span><span>{profile.nickname}</span></div></>}</div></header><main className="app-main">{error && <div className="alert error page-alert" role="alert"><span>{error}</span><button className="icon-button" aria-label="Dismiss message" onClick={() => setError('')}><Icon name="close" size={16}/></button></div>}{!bootstrap.session.setup_complete || !profile ? <Onboarding onDone={(value) => { acceptBootstrap(value); setPage('home'); }}/>: page === 'parent-gate' ? <ParentGate onBack={() => void home()} onBusy={(busy) => { requestInFlight.current = busy; if (busy) refreshGeneration.current += 1; setPending(busy ? 'unlock' : ''); }} onUnlock={(value, seconds) => { setParentOverview(value); setParentUntil(Date.now() + seconds * 1000); setPage('parent'); }}/>: page === 'parent' && parentOverview ? <ParentView overview={parentOverview} save={(value) => void saveSettings(value)} onExport={() => void exportData()} onDelete={() => void deleteProfile()} onLock={() => void home()} pending={pending} message={parentMessage}/>: page === 'lesson' && lesson ? <LessonView lesson={lesson} intro={intro} setIntro={setIntro} pending={pending} answer={(value) => void answer(value)} next={() => void next()} hint={() => void hint()} home={home} finalFeedback={finalFeedback} voice={{ enabled: profile.voice_enabled, blocked: bootstrap.break.due || (!!pending && pending !== 'narration'), prepare: prepareNarration }}/>: pending === 'lesson' ? <div className="loading-view"><span className="spinner"/>Opening your discovery…</div>: <Dashboard bootstrap={bootstrap} openLesson={(id) => void openLesson(id)} takeBreak={() => void breakAction('start')}/>}<footer className="footer"><span><span className="mini-brand">tarka.</span>A little wonder. A world to learn.</span><span><Icon name="heart" size={12}/>Made for curious minds, at their own pace.</span></footer></main>{profile && bootstrap.break.due && !parentPage && <BreakDialog state={bootstrap.break} pending={pending} start={() => void breakAction('start')} finish={() => void breakAction('finish')} parent={openParent} error={error}/>}</div>;
}
