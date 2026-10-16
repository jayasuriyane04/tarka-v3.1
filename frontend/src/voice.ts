import type { Narration } from './types';

export type DeviceVoice = { voiceURI: string; name: string; lang: string; localService: boolean; default: boolean };
export type VoiceStatus = 'idle' | 'preparing' | 'speaking' | 'paused' | 'finished' | 'error';
export type VoiceState = { status: VoiceStatus; narration: Narration | null; error: string };
export interface SpeechAdapter {
  voices(): DeviceVoice[];
  speak(text: string, voiceURI: string, rate: number, callbacks: { start: () => void; end: () => void; error: () => void }): void;
  cancel(): void;
  pause(): void;
  resume(): void;
}

// Never fall back to an unspecified default voice: a browser may choose a remote service.
export function localEnglishVoices(voices: DeviceVoice[]): DeviceVoice[] {
  return voices.filter((voice) => voice.localService === true && /^en(?:[-_]|$)/i.test(voice.lang))
    .sort((a, b) => Number(b.default) - Number(a.default) || a.name.localeCompare(b.name));
}

export function speechChunks(text: string, limit = 220): string[] {
  const chunks: string[] = [];
  let current = '';
  for (const word of text.trim().split(/\s+/)) {
    if (current && current.length + word.length + 1 > limit) { chunks.push(current); current = ''; }
    current += `${current ? ' ' : ''}${word}`;
  }
  if (current) chunks.push(current);
  return chunks;
}

export function browserSpeechAdapter(): SpeechAdapter | null {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) return null;
  const synth = window.speechSynthesis;
  // Retain the current utterance until its end/cancel event on engines that need this.
  let current: SpeechSynthesisUtterance | null = null;
  return {
    voices: () => synth.getVoices(),
    speak(text, voiceURI, rate, callbacks) {
      const voice = localEnglishVoices(synth.getVoices()).find((item) => item.voiceURI === voiceURI);
      if (!voice) { callbacks.error(); return; }
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = voice as SpeechSynthesisVoice;
      utterance.lang = voice.lang;
      utterance.rate = rate;
      utterance.onstart = callbacks.start;
      utterance.onend = () => { if (current === utterance) current = null; callbacks.end(); };
      utterance.onerror = () => { if (current === utterance) current = null; callbacks.error(); };
      current = utterance;
      synth.speak(utterance);
    },
    // Cancel clears the queue but does not reset the synthesis engine's paused flag.
    cancel: () => { synth.cancel(); synth.resume(); current = null; },
    pause: () => synth.pause(),
    resume: () => synth.resume(),
  };
}

/** Owns one narration. Late HTTP responses and speech callbacks cannot restart a cancelled lesson. */
export class VoiceController {
  private generation = 0;
  private state: VoiceState = { status: 'idle', narration: null, error: '' };
  private startTimer: ReturnType<typeof setTimeout> | undefined;
  private resumeNext: (() => void) | null = null;
  constructor(private adapter: SpeechAdapter, private changed: (state: VoiceState) => void) {}
  private publish(update: Partial<VoiceState>) { this.state = { ...this.state, ...update }; this.changed(this.state); }
  private clearTimer() { if (this.startTimer) clearTimeout(this.startTimer); this.startTimer = undefined; }
  stop(clearTranscript = false) {
    this.generation += 1;
    this.clearTimer();
    this.resumeNext = null;
    this.adapter.cancel();
    this.publish({ status: 'idle', error: '', ...(clearTranscript ? { narration: null } : {}) });
  }
  dispose() { this.generation += 1; this.clearTimer(); this.resumeNext = null; this.adapter.cancel(); }
  pause() { if (this.state.status === 'speaking') { this.publish({ status: 'paused' }); this.adapter.pause(); } }
  resume() {
    if (this.state.status !== 'paused') return;
    const next = this.resumeNext;
    this.resumeNext = null;
    this.publish({ status: 'speaking' });
    this.adapter.resume();
    next?.();
  }
  async play(prepare: () => Promise<Narration>, voiceURI: string, rate: number) {
    this.stop(true);
    const generation = this.generation;
    const fail = (message: string) => {
      if (generation !== this.generation) return;
      this.generation += 1;
      this.clearTimer();
      this.resumeNext = null;
      this.adapter.cancel();
      this.publish({ status: 'error', error: message });
    };
    if (!localEnglishVoices(this.adapter.voices()).some((voice) => voice.voiceURI === voiceURI)) {
      fail('No local English voice is available. You can keep learning with the text.'); return;
    }
    this.publish({ status: 'preparing' });
    try {
      const narration = await prepare();
      if (generation !== this.generation) return;
      if (!narration.text.trim() || narration.text.length > 12000) throw new Error('This passage is not ready to read aloud. Please use the lesson text.');
      this.publish({ narration });
      const chunks = speechChunks(narration.text);
      const speak = (index: number) => {
        if (generation !== this.generation) return;
        if (index >= chunks.length) { this.publish({ status: 'finished' }); return; }
        // Availability may change after permission checks or between chunks.
        if (!localEnglishVoices(this.adapter.voices()).some((voice) => voice.voiceURI === voiceURI)) {
          fail('The device voice is no longer available. Please use the transcript.'); return;
        }
        this.startTimer = setTimeout(() => fail('The device voice did not start. Please use the transcript or try Play again.'), 15000);
        this.adapter.speak(chunks[index], voiceURI, Math.min(1.15, Math.max(0.7, rate)), {
          start: () => {
            if (generation !== this.generation) return;
            this.clearTimer();
            if (this.state.status !== 'paused') this.publish({ status: 'speaking' });
          },
          end: () => {
            if (generation !== this.generation) return;
            this.clearTimer();
            if (this.state.status === 'paused') this.resumeNext = () => speak(index + 1);
            else speak(index + 1);
          },
          error: () => fail('The device voice could not play. Your lesson and transcript are still here.'),
        });
      };
      speak(0);
    } catch (error) { fail(error instanceof Error ? error.message : 'Read-aloud is unavailable. You can continue with the lesson text.'); }
  }
}
