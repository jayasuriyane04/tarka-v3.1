import { afterEach, describe, expect, it, vi } from 'vitest';
import { browserSpeechAdapter, localEnglishVoices, speechChunks, VoiceController, type DeviceVoice, type SpeechAdapter, type VoiceState } from './voice';
import type { Narration } from './types';

const local: DeviceVoice = { voiceURI: 'device-one', name: 'Device English', lang: 'en-IN', localService: true, default: true };
const narration: Narration = { text: 'Look at two groups. Count how many objects are in each group.', label: 'The idea', source: 'lesson', question_id: 'q1' };
function setup() {
  const states: VoiceState[] = [];
  const calls: { text: string; uri: string; rate: number; callbacks: Parameters<SpeechAdapter['speak']>[3] }[] = [];
  const adapter: SpeechAdapter = {
    voices: vi.fn(() => [local]),
    speak: vi.fn((text, uri, rate, callbacks) => calls.push({ text, uri, rate, callbacks })),
    cancel: vi.fn(), pause: vi.fn(), resume: vi.fn(),
  };
  const controller = new VoiceController(adapter, (value) => states.push(value));
  return { controller, adapter, calls, states, last: () => states.at(-1)! };
}
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

describe('browser speech adapter', () => {
  it('resets a paused engine after Stop so a new Play can start', async () => {
    let paused = false;
    const spoken: string[] = [];
    class FakeUtterance {
      onstart?: () => void;
      constructor(public text: string) {}
    }
    const synth = {
      getVoices: () => [local],
      speak: (utterance: FakeUtterance) => {
        if (!paused) { spoken.push(utterance.text); utterance.onstart?.(); }
      },
      cancel: vi.fn(), // The real API removes utterances without clearing paused.
      pause: () => { paused = true; },
      resume: () => { paused = false; },
    };
    vi.stubGlobal('window', { speechSynthesis: synth, SpeechSynthesisUtterance: FakeUtterance });
    vi.stubGlobal('SpeechSynthesisUtterance', FakeUtterance);
    const states: VoiceState[] = [];
    const controller = new VoiceController(browserSpeechAdapter()!, (state) => states.push(state));
    await controller.play(async () => narration, local.voiceURI, 0.9);
    controller.pause();
    expect(paused).toBe(true);
    controller.stop();
    await controller.play(async () => narration, local.voiceURI, 0.9);
    expect(spoken).toEqual([narration.text, narration.text]);
    expect(states.at(-1)?.status).toBe('speaking');
    controller.dispose();
  });
});

describe('private device voice selection', () => {
  it('excludes remote, unknown-locality and non-English voices even if default', () => {
    const voices = [
      { ...local, localService: false, voiceURI: 'remote' },
      { ...local, localService: undefined, voiceURI: 'unknown' } as unknown as DeviceVoice,
      { ...local, lang: 'fr-FR', voiceURI: 'french' }, local,
    ];
    expect(localEnglishVoices(voices).map((voice) => voice.voiceURI)).toEqual(['device-one']);
  });
  it('splits long narration without losing or reordering words', () => {
    const text = `${'A useful idea has room for thinking. '.repeat(50)}Finished.`;
    const chunks = speechChunks(text);
    expect(chunks.length).toBeGreaterThan(1);
    expect(chunks.every((chunk) => chunk.length <= 220)).toBe(true);
    expect(chunks.join(' ')).toBe(text.trim());
  });
});

describe('speech controller lifecycle', () => {
  it('keeps a chunk-boundary pause until explicit Resume', async () => {
    const { controller, calls, last } = setup();
    await controller.play(async () => ({ ...narration, text: 'Think carefully about each group. '.repeat(20) }), local.voiceURI, 0.9);
    calls[0].callbacks.start();
    controller.pause();
    calls[0].callbacks.start(); // A queued engine event must not undo Pause.
    calls[0].callbacks.end();
    expect(last().status).toBe('paused');
    expect(calls).toHaveLength(1);
    controller.resume();
    expect(calls).toHaveLength(2);
    calls[1].callbacks.start();
    expect(last().status).toBe('speaking');
    controller.dispose();
  });
  it('does not prepare or speak until explicit play, and requires server preparation before speaking', async () => {
    const { controller, calls, last } = setup();
    expect(calls).toEqual([]);
    let resolve!: (value: Narration) => void;
    const run = controller.play(() => new Promise((done) => { resolve = done; }), local.voiceURI, 0.9);
    expect(last().status).toBe('preparing');
    expect(calls).toHaveLength(0);
    resolve(narration); await run;
    expect(calls[0].text).toBe(narration.text);
    expect(last().narration).toEqual(narration);
    calls[0].callbacks.start(); expect(last().status).toBe('speaking');
    calls[0].callbacks.end(); expect(last().status).toBe('finished');
    controller.dispose();
  });
  it('never sends a request or speaks when no permitted local voice exists', async () => {
    const { controller, adapter, calls, last } = setup();
    vi.mocked(adapter.voices).mockReturnValue([{ ...local, localService: false }]);
    const prepare = vi.fn(async () => narration);
    await controller.play(prepare, local.voiceURI, 0.9);
    expect(prepare).not.toHaveBeenCalled(); expect(calls).toHaveLength(0);
    expect(last().error).toContain('No local English voice');
    controller.dispose();
  });
  it.each(['stop', 'dispose'] as const)('ignores a late server response after %s', async (method) => {
    const { controller, calls } = setup();
    let resolve!: (value: Narration) => void;
    const run = controller.play(() => new Promise((done) => { resolve = done; }), local.voiceURI, 0.9);
    controller[method](); resolve(narration); await run;
    expect(calls).toHaveLength(0);
  });
  it('ignores old utterance callbacks after a new lesson starts', async () => {
    const { controller, calls, last } = setup();
    await controller.play(async () => narration, local.voiceURI, 0.9);
    const old = calls[0].callbacks;
    controller.stop(true);
    await controller.play(async () => ({ ...narration, text: 'A new question.', question_id: 'q2' }), local.voiceURI, 0.9);
    old.error(); old.end(); old.start();
    expect(calls).toHaveLength(2); expect(last().narration?.question_id).toBe('q2');
    expect(last().error).toBe('');
    controller.dispose();
  });
  it('supports pause and resume without a new request, and stop clears queued chunks', async () => {
    const { controller, adapter, calls, last } = setup();
    const prepare = vi.fn(async () => ({ ...narration, text: 'Think carefully about each group. '.repeat(30) }));
    await controller.play(prepare, local.voiceURI, 0.9);
    calls[0].callbacks.start(); controller.pause();
    expect(adapter.pause).toHaveBeenCalledOnce(); expect(last().status).toBe('paused');
    controller.resume(); expect(adapter.resume).toHaveBeenCalledOnce(); expect(last().status).toBe('speaking');
    expect(prepare).toHaveBeenCalledOnce();
    controller.stop(); calls[0].callbacks.end();
    expect(calls).toHaveLength(1); expect(last().status).toBe('idle');
  });
  it('speaks long content sequentially with the same explicit voice and bounded pace', async () => {
    const { controller, calls, last } = setup();
    const text = 'Think carefully about each group. '.repeat(20).trim();
    await controller.play(async () => ({ ...narration, text }), local.voiceURI, 99);
    for (let index = 0; index < calls.length; index += 1) { calls[index].callbacks.start(); calls[index].callbacks.end(); }
    expect(calls.length).toBeGreaterThan(1);
    expect(calls.map((call) => call.text).join(' ')).toBe(text);
    expect(calls.every((call) => call.uri === local.voiceURI && call.rate === 1.15)).toBe(true);
    expect(last().status).toBe('finished'); controller.dispose();
  });
  it('fails safely if a permitted voice disappears during preparation', async () => {
    const { controller, adapter, calls, last } = setup();
    await controller.play(async () => { vi.mocked(adapter.voices).mockReturnValue([]); return narration; }, local.voiceURI, 0.9);
    expect(calls).toHaveLength(0); expect(last().narration).toEqual(narration);
    expect(last().error).toContain('no longer available'); controller.dispose();
  });
  it('keeps a visible transcript when the audio engine errors', async () => {
    const { controller, calls, last } = setup();
    await controller.play(async () => narration, local.voiceURI, 0.9);
    calls[0].callbacks.error(); expect(last().status).toBe('error');
    expect(last().narration).toEqual(narration);
    calls[0].callbacks.end(); expect(calls).toHaveLength(1); controller.dispose();
  });
  it('times out a silent engine without queuing further speech', async () => {
    vi.useFakeTimers();
    const { controller, calls, last } = setup();
    await controller.play(async () => narration, local.voiceURI, 0.9);
    vi.advanceTimersByTime(15000);
    expect(last().error).toContain('did not start');
    calls[0].callbacks.start(); expect(last().status).toBe('error'); controller.dispose();
  });
  it('surfaces preparation errors with no unapproved speech', async () => {
    const { controller, calls, last } = setup();
    await controller.play(async () => { throw new Error('Time for a break.'); }, local.voiceURI, 0.9);
    expect(calls).toHaveLength(0); expect(last().error).toBe('Time for a break.'); controller.dispose();
  });
  it('requests authorization again when replaying, rather than caching a past permission', async () => {
    const { controller } = setup();
    const prepare = vi.fn(async () => narration);
    await controller.play(prepare, local.voiceURI, 0.9); controller.stop();
    await controller.play(prepare, local.voiceURI, 0.9);
    expect(prepare).toHaveBeenCalledTimes(2); controller.dispose();
  });
});
