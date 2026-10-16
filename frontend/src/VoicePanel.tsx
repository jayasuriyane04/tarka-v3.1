import { useEffect, useRef, useState } from 'react';
import { browserSpeechAdapter, localEnglishVoices, VoiceController, type DeviceVoice, type VoiceState } from './voice';
import type { Lesson, Narration, NarrationRequest } from './types';

export type VoicePanelProps = {
  lesson: Lesson; intro: boolean; enabled: boolean; blocked: boolean;
  prepare: (request: NarrationRequest) => Promise<Narration>;
};

export function narrationChoices(lesson: Lesson, intro: boolean): { key: string; label: string; request: NarrationRequest }[] {
  const choices: { key: string; label: string; request: NarrationRequest }[] = [];
  const add = (segment: NarrationRequest['segment'], label: string, hint_level?: 1 | 2 | 3) => choices.push({ key: `${segment}${hint_level ?? ''}`, label, request: { lesson_id: lesson.id, segment, ...(hint_level ? { hint_level } : {}) } });
  if (!lesson.state.completed) {
    if (intro && lesson.question?.kind !== 'transfer') add('lesson', 'Teach the idea & example');
    else if (lesson.question) add('question', 'Read the question & choices');
    for (const hint of lesson.hints) if ([1, 2, 3].includes(hint.level)) add('hint', `Read hint ${hint.level}`, hint.level as 1 | 2 | 3);
  }
  if (lesson.last_feedback) add('feedback', 'Explain the checked feedback');
  return choices;
}

export function VoicePanel({ lesson, intro, enabled, blocked, prepare }: VoicePanelProps) {
  const [voices, setVoices] = useState<DeviceVoice[]>([]);
  const [supported, setSupported] = useState<boolean | null>(null);
  const [voiceURI, setVoiceURI] = useState('');
  const [rate, setRate] = useState(0.9);
  const [selection, setSelection] = useState('');
  const [state, setState] = useState<VoiceState>({ status: 'idle', narration: null, error: '' });
  const controller = useRef<VoiceController | null>(null);
  const choices = narrationChoices(lesson, intro);
  const choice = choices.find((item) => item.key === selection) ?? choices[0];
  const voice = voices.find((item) => item.voiceURI === voiceURI) ?? voices[0];
  const context = `${lesson.id}:${lesson.question?.id ?? 'complete'}:${intro}:${lesson.state.tries}:${lesson.state.answered}:${lesson.state.completed}:${lesson.hints.length}:${enabled}:${blocked}`;
  useEffect(() => {
    const adapter = browserSpeechAdapter();
    setSupported(!!adapter);
    if (!adapter) return;
    const instance = new VoiceController(adapter, setState);
    controller.current = instance;
    const updateVoices = () => {
      const available = localEnglishVoices(adapter.voices());
      setVoices(available);
      // A changed installed-voice list must never silently select another voice mid-play.
      instance.stop();
    };
    const hidden = () => { if (document.hidden) instance.stop(); };
    const leave = () => instance.stop();
    updateVoices();
    window.speechSynthesis.addEventListener('voiceschanged', updateVoices);
    document.addEventListener('visibilitychange', hidden);
    window.addEventListener('pagehide', leave);
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', updateVoices);
      document.removeEventListener('visibilitychange', hidden);
      window.removeEventListener('pagehide', leave);
      instance.dispose(); controller.current = null;
    };
  }, []);
  useEffect(() => { controller.current?.stop(true); setSelection(''); }, [context]);
  const active = ['preparing', 'speaking', 'paused'].includes(state.status);
  const canPlay = enabled && !blocked && !!voice && !!choice && !active;
  function play() {
    if (!canPlay || !choice || !voice || document.hidden) return;
    const expectedQuestion = lesson.question?.id;
    void controller.current?.play(async () => {
      const result = await prepare(choice.request);
      if (expectedQuestion && result.question_id !== expectedQuestion) throw new Error('The question has changed. Choose Play again for the current question.');
      return result;
    }, voice.voiceURI, rate);
  }
  return <section className="card voice-card" aria-label="Listen and learn">
    <div className="voice-heading"><span className="voice-symbol" aria-hidden="true">♪</span><span className="pill teal">Device voice</span></div>
    <h2>Listen. Pause. Think.</h2>
    <p>A voice can read the idea with you. The words stay here to follow at your own pace.</p>
    {!enabled ? <p className="voice-notice">A grown-up can turn on read-aloud in Parent space. Every lesson also works with text.</p> : <>
      {supported === false ? <p className="voice-notice" role="status">This browser does not support read-aloud. You can keep learning with the lesson text.</p> : supported && !voices.length ? <p className="voice-notice" role="status">No local English voice is available yet. Your grown-up can check device speech settings. We use only voices this browser identifies as local; text learning is ready now.</p> : null}
      <label className="field"><span>What shall we read?</span><select value={choice?.key ?? ''} disabled={blocked || !choices.length} onChange={(event) => { controller.current?.stop(true); setSelection(event.target.value); }}>{choices.length ? choices.map((item) => <option key={item.key} value={item.key}>{item.label}</option>) : <option value="">Choose a lesson step first</option>}</select></label>
      <div className="voice-settings"><label className="field"><span>Voice</span><select value={voice?.voiceURI ?? ''} disabled={!voices.length || blocked} onChange={(event) => { controller.current?.stop(); setVoiceURI(event.target.value); }}>{voices.length ? voices.map((item) => <option key={item.voiceURI} value={item.voiceURI}>{item.name} · {item.lang}</option>) : <option value="">No local voice</option>}</select></label><label className="field"><span>Pace</span><select value={rate} disabled={blocked} onChange={(event) => { controller.current?.stop(); setRate(Number(event.target.value)); }}><option value={0.75}>Gentle</option><option value={0.9}>Steady</option><option value={1.05}>Brisk</option></select></label></div>
      <div className="voice-controls"><button className="button primary" disabled={!canPlay} onClick={play}>{state.status === 'preparing' ? 'Getting the words…' : 'Play'}<span aria-hidden="true">▷</span></button>{state.status === 'paused' ? <button className="button ghost" disabled={blocked} onClick={() => controller.current?.resume()}>Resume</button> : <button className="button ghost" disabled={state.status !== 'speaking' || blocked} onClick={() => controller.current?.pause()}>Pause</button>}<button className="button ghost" disabled={!active} onClick={() => controller.current?.stop()}>Stop</button></div>
      <p className="voice-status" role="status">{state.status === 'speaking' ? 'Reading aloud. Pause whenever you want to think.' : state.status === 'paused' ? 'Paused. Your time to think.' : state.status === 'finished' ? 'Finished reading. What did you notice?' : state.status === 'preparing' ? 'Preparing this lesson’s words…' : 'Press Play when you are ready. Nothing plays automatically.'}</p>
      {state.error && <p className="alert error" role="alert">{state.error}</p>}
      {lesson.question?.kind === 'transfer' && !lesson.state.answered && <p className="voice-notice">Reading this new question aloud counts as support. We’ll record a supported attempt, even if sound cannot play.</p>}
      {lesson.state.voice_assisted && <p className="quiet">Read-aloud support is recorded for this question.</p>}
      {state.narration && <div className="voice-transcript"><h3>Words to follow · {state.narration.label}</h3><p>{state.narration.text}</p><span className="hint-source">{state.narration.source === 'nebius' ? 'NVIDIA-selected written hint' : 'Written lesson content'} · spoken by your device</span></div>}
    </>}
    <p className="voice-privacy">No microphone or voice recording. Device speech is separate from NVIDIA hint selection.</p>
  </section>;
}
