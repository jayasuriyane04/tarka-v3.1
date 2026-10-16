import { describe, expect, it } from 'vitest';
import { lessonEvidence } from './types';
describe('learning evidence display', () => {
  it('does not equate a supported completion with independent understanding', () => {
    expect(lessonEvidence({ completed: true, transfer_independent: false })).toBe('Practised with support');
  });
  it('shows independent evidence only when the server supplies it', () => {
    expect(lessonEvidence({ completed: true, transfer_independent: true })).toBe('Independent transfer');
  });
  it('does not infer completion from absence of attempts', () => {
    expect(lessonEvidence({ completed: false, transfer_independent: false })).toBe('Ready to explore');
  });
});
