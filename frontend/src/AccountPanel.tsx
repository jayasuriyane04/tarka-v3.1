import { useId, useRef, useState, type FormEvent } from 'react';
import { Icon } from './art';
import { passwordProblem } from './AuthPanel';
import './auth.css';

export type PasswordChange = { current_password: string; new_password: string };
export type AccountPanelProps = {
  username: string;
  onLogout: () => Promise<void>;
  onLogoutAll: () => Promise<void>;
  onPassword: (passwords: PasswordChange) => Promise<void>;
};

export function validatePasswordChange(current: string, password: string, confirmation: string): string | null {
  if (!current) return 'Enter your current password.';
  const problem = passwordProblem(password);
  if (problem) return problem;
  if (current === password) return 'Choose a new password that is different from your current one.';
  if (password !== confirmation) return 'The new passwords do not match. Enter the same password in both boxes.';
  return null;
}

export function AccountPanel({ username, onLogout, onLogoutAll, onPassword }: AccountPanelProps) {
  const id = useId();
  const [current, setCurrent] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [pending, setPending] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const submitting = useRef(false);

  async function action(name: string, operation: () => Promise<void>) {
    if (submitting.current) return;
    submitting.current = true; setPending(name); setError(''); setMessage('');
    try {
      await operation();
      if (name === 'password') { setCurrent(''); setPassword(''); setConfirmation(''); setMessage('Your password has been changed, and other devices have been signed out. Save the new password somewhere safe.'); }
    } catch (err) { setError(err instanceof Error ? err.message : 'The account change could not be completed. Please try again.'); }
    finally { submitting.current = false; setPending(''); }
  }

  function changePassword(event: FormEvent) {
    event.preventDefault();
    if (submitting.current) return;
    const problem = validatePasswordChange(current, password, confirmation);
    if (problem) { setError(problem); setMessage(''); return; }
    void action('password', () => onPassword({ current_password: current, new_password: password }));
  }

  return <section className="card parent-section account-panel" aria-labelledby={`${id}-heading`} aria-busy={!!pending}>
    <span className="pill purple"><Icon name="lock" size={13}/>Parent account</span>
    <h2 id={`${id}-heading`}>Your sign-in and security</h2>
    <p>Signed in as <strong className="account-username">{username}</strong>. Keep this account for a parent or caregiver.</p>
    <div className="account-session-actions">
      <button className="button secondary" type="button" disabled={!!pending} onClick={() => void action('logout', onLogout)}>{pending === 'logout' ? 'Signing out…' : 'Sign out on this device'}</button>
      <button className="button secondary" type="button" disabled={!!pending} onClick={() => void action('logout-all', onLogoutAll)}>{pending === 'logout-all' ? 'Signing out everywhere…' : 'Sign out on all devices'}</button>
    </div>
    <p className="quiet">Signing out keeps your saved learning record. Sign in again to return to it.</p>
    <form className="account-password-form" onSubmit={changePassword}>
      <fieldset className="auth-fields" disabled={!!pending}>
        <legend>Change account password</legend>
        <input type="text" name="username" autoComplete="username" value={username} readOnly hidden/>
        <label className="field" htmlFor={`${id}-current`}><span>Current password</span><input id={`${id}-current`} name="current-password" type="password" autoComplete="current-password" maxLength={128} value={current} onChange={(event) => setCurrent(event.target.value)} required/></label>
        <label className="field" htmlFor={`${id}-new`}><span>New password</span><input id={`${id}-new`} name="new-password" type="password" autoComplete="new-password" maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} required aria-describedby={`${id}-password-help`}/><small id={`${id}-password-help`}>Use 15–128 characters. A few unrelated words can make a memorable passphrase.</small></label>
        <label className="field" htmlFor={`${id}-confirm`}><span>Confirm new password</span><input id={`${id}-confirm`} name="confirm-new-password" type="password" autoComplete="new-password" maxLength={128} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required/></label>
        <p className="quiet">Changing your password signs out your other devices. This device stays signed in.</p>
        <button className="button primary" type="submit">{pending === 'password' ? 'Changing password…' : 'Change password'}</button>
      </fieldset>
    </form>
    {error && <div className="alert error" role="alert">{error}</div>}
    {message && <p className="parent-success" role="status">{message}</p>}
    <p className="auth-recovery quiet">No self-service password recovery is available. Save your password securely; your parent PIN cannot reset it.</p>
  </section>;
}
