import { afterEach, describe, expect, it, vi } from 'vitest';
import { api, ApiError, setCsrfToken, setParentToken } from './api';

afterEach(() => { vi.unstubAllGlobals(); setCsrfToken(''); setParentToken(''); });
function respond(body: unknown, status = 200) {
  const fetch = vi.fn().mockImplementation(async () => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }));
  vi.stubGlobal('fetch', fetch);
  return fetch;
}
describe('browser API security boundary', () => {
  it('sends the parent capability only to parent endpoints and the CSRF token on writes', async () => {
    const fetch = respond({}); setCsrfToken('csrf'); setParentToken('parent');
    await api('/answer', { choice: 1 });
    expect(fetch.mock.calls[0][1].headers).toEqual({ 'Content-Type': 'application/json', 'X-CSRF-Token': 'csrf' });
    await api('/parent/lock', {});
    expect(fetch.mock.calls[1][1].headers).toEqual({ 'Content-Type': 'application/json', 'X-CSRF-Token': 'csrf', 'X-Parent-Token': 'parent' });
    expect(fetch.mock.calls[1][1].credentials).toBe('include');
  });
  it('stops sending the capability once cleared from memory', async () => {
    const fetch = respond({}); setParentToken('parent'); setParentToken('');
    await api('/parent/overview');
    expect(fetch.mock.calls[0][1].headers).not.toHaveProperty('X-Parent-Token');
  });
  it('preserves break and authorization status codes for the app to handle', async () => {
    respond({ detail: 'Pause first.' }, 423);
    await expect(api('/answer', {})).rejects.toMatchObject({ status: 423, message: 'Pause first.' });
  });
  it('does not expose a provider or proxy HTML error document', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<h1>Internal private detail</h1>', { status: 502, headers: { 'Content-Type': 'text/html' } })));
    await expect(api('/bootstrap')).rejects.toBeInstanceOf(ApiError);
    await expect(api('/bootstrap')).rejects.not.toThrow('Internal private detail');
  });
});
