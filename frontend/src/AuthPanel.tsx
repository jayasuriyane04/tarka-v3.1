import { useId, useRef, useState, type FormEvent } from 'react';
import { Icon } from './art';
import './auth.css';

export type AuthMode = 'register' | 'login';
export type AuthCredentials = { username: string; password: string };
export type AuthRegistration = AuthCredentials & { adult_confirmed: true; existing_pin?: string };
export type AuthPanelProps = {
  initialMode?: AuthMode;
  legacyProfile: boolean;
  submit: (endpoint: AuthMode, data: AuthCredentials | AuthRegistration) => Promise<void>;
  onCancel?: () => void;
};

export function passwordProblem(password: string): string | null {
  const length = Array.from(password).length;
  if (length < 15 || length > 128) return 'Use a password between 15 and 128 characters. A few unrelated words can make a memorable passphrase.';
  return null;
}

export function validateRegistration(data: {
  username: string; password: string; confirmation: string; adult: boolean; legacyProfile: boolean; pin: string;
}): string | null {
  if (!/^[A-Za-z0-9_]{3,32}$/.test(data.username.trim())) return 'Choose a username with 3–32 letters, numbers or underscores.';
  const problem = passwordProblem(data.password);
  if (problem) return problem;
  if (data.password !== data.confirmation) return 'The passwords do not match. Enter the same password in both boxes.';
  if (!data.adult) return 'An adult parent or caregiver must create the account.';
  if (data.legacyProfile && !/^\d{6}$/.test(data.pin)) return 'Enter the existing six-digit parent PIN to keep this learner’s progress.';
  return null;
}

export function AuthPanel({ initialMode = 'register', legacyProfile, submit, onCancel }: AuthPanelProps) {
  const id = useId();
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [pin, setPin] = useState('');
  const [adult, setAdult] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const [visible, setVisible] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const submitting = useRef(false);
  const registering = mode === 'register';

  function changeMode(nextMode: AuthMode) {
    if (submitting.current) return;
    setMode(nextMode); setPassword(''); setConfirmation(''); setPin('');
    setAdult(false); setAcknowledged(false); setVisible(false); setError('');
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (submitting.current) return;
    setError('');
    const problem = registering
      ? validateRegistration({ username, password, confirmation, adult, legacyProfile, pin })
      : (!username.trim() || !password ? 'Enter your username and password.' : legacyProfile && !acknowledged ? 'Confirm that signing in switches to the account’s learning record.' : null);
    if (problem) { setError(problem); return; }
    submitting.current = true; setPending(true);
    try {
      const credentials = { username: username.trim(), password };
      await submit(mode, registering
        ? { ...credentials, adult_confirmed: true, ...(legacyProfile ? { existing_pin: pin } : {}) }
        : credentials);
      setPassword(''); setConfirmation(''); setPin('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The account request could not be completed. Please try again.');
    } finally { submitting.current = false; setPending(false); }
  }

  return <section className="card auth-panel" aria-labelledby={`${id}-heading`}>
    <span className="pill purple"><Icon name="shield" size={14}/>For a parent or caregiver</span>
    <h1 id={`${id}-heading`}>{registering ? 'A home for their discoveries.' : 'Welcome back.'}</h1>
    <p>{registering ? 'Create your parent account to return to your learner’s progress on this device or another.' : 'Sign in with your parent account to continue learning.'}</p>
    <div className="auth-mode" aria-label="Account action">
      <button type="button" aria-pressed={registering} disabled={pending} onClick={() => changeMode('register')}>Create account</button>
      <button type="button" aria-pressed={!registering} disabled={pending} onClick={() => changeMode('login')}>Sign in</button>
    </div>
    <form onSubmit={(event) => void handleSubmit(event)} aria-busy={pending}>
      <fieldset className="auth-fields" disabled={pending}>
        <legend className="sr-only">{registering ? 'Create a parent account' : 'Sign in to your parent account'}</legend>
        {legacyProfile && <p className="auth-notice">{registering
          ? 'Keep the progress already on this browser. Your existing parent PIN confirms that this learning record belongs to you.'
          : 'Signing in opens that account’s learner. This browser’s unlinked learning record will not be merged. To keep this record, create an account here first.'}</p>}
        <label className="field" htmlFor={`${id}-username`}><span>Parent username</span>
          <input id={`${id}-username`} name="username" autoComplete="username" autoCapitalize="none" spellCheck={false} maxLength={32} minLength={registering ? 3 : undefined} pattern={registering ? '[A-Za-z0-9_]{3,32}' : undefined} value={username} onChange={(event) => setUsername(event.target.value)} required aria-describedby={`${id}-username-help`}/>
          <small id={`${id}-username-help`}>{registering ? '3–32 letters, numbers or underscores. Use a made-up username, not your child’s name. No email needed.' : 'Use the username you chose when you created your account.'}</small>
        </label>
        <label className="field" htmlFor={`${id}-password`}><span>Password</span>
          <input id={`${id}-password`} name="password" type={visible ? 'text' : 'password'} autoComplete={registering ? 'new-password' : 'current-password'} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} required aria-describedby={registering ? `${id}-password-help` : undefined}/>
          {registering && <small id={`${id}-password-help`}>15–128 characters. Try a few unrelated words, and save the password in your password manager.</small>}
        </label>
        {registering && <label className="field" htmlFor={`${id}-confirm`}><span>Confirm password</span>
          <input id={`${id}-confirm`} name="confirm-password" type={visible ? 'text' : 'password'} autoComplete="new-password" maxLength={128} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required/>
        </label>}
        <label className="auth-check"><input type="checkbox" checked={visible} onChange={(event) => setVisible(event.target.checked)}/><span>Show {registering ? 'passwords' : 'password'}</span></label>
        {registering && legacyProfile && <label className="field" htmlFor={`${id}-pin`}><span>Existing parent PIN · 6 digits</span>
          <input id={`${id}-pin`} name="existing-pin" type="password" inputMode="numeric" autoComplete="off" pattern="[0-9]{6}" minLength={6} maxLength={6} value={pin} onChange={(event) => setPin(event.target.value.replace(/\D/g, ''))} required/>
        </label>}
        {registering ? <label className="consent-option"><input type="checkbox" checked={adult} onChange={(event) => setAdult(event.target.checked)} required/><span>I am an adult parent or caregiver creating this account. I will guide my child’s use of Tarka.</span></label>
          : legacyProfile && <label className="consent-option"><input type="checkbox" checked={acknowledged} onChange={(event) => setAcknowledged(event.target.checked)} required/><span>I understand that signing in switches learning records.</span></label>}
        {error && <div className="alert error" role="alert">{error}</div>}
        <button className="button primary auth-submit" type="submit">{pending ? (registering ? 'Creating account…' : 'Signing in…') : (registering ? 'Create account' : 'Sign in')}<Icon name="arrow" size={16}/></button>
      </fieldset>
    </form>
    <p className="auth-footnote"><Icon name="lock" size={14}/>The account password protects sign-in. The separate parent PIN protects household settings.</p>
    <p className="quiet auth-recovery">No self-service password recovery is available. Keep your sign-in details somewhere safe; your parent PIN cannot reset the account password.</p>
    {onCancel && <button className="text-button auth-cancel" type="button" disabled={pending} onClick={onCancel}>Back to Tarka</button>}
  </section>;
}
