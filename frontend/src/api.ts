let csrfToken = '';
let parentToken = '';
export const setCsrfToken = (value: string) => { csrfToken = value; };
export const setParentToken = (value: string) => { parentToken = value; };
export class ApiError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function api<T>(path: string, data?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method: data === undefined ? 'GET' : 'POST', credentials: 'include', signal: AbortSignal.timeout(45000),
    headers: { ...(data === undefined ? {} : { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken }), ...(path.startsWith('/parent/') && parentToken ? { 'X-Parent-Token': parentToken } : {}) },
    ...(data === undefined ? {} : { body: JSON.stringify(data) }),
  });
  if (!response.headers.get('content-type')?.includes('application/json')) throw new ApiError('We cannot reach this learning space right now. Please try again in a moment.', response.status);
  const result = await response.json();
  if (!response.ok) throw new ApiError(typeof result.detail === 'string' ? result.detail : 'That could not be saved. Please try again.', response.status);
  return result as T;
}
