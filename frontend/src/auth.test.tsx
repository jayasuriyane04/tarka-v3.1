import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { AuthPanel, passwordProblem, validateRegistration } from './AuthPanel';
import { AccountPanel, validatePasswordChange } from './AccountPanel';

const noop = async () => undefined;
const valid = { username: 'parent_garden', password: 'sunflower moss paper boat', confirmation: 'sunflower moss paper boat', adult: true, legacyProfile: false, pin: '' };

describe('parent account forms', () => {
  it('offers functional form controls for account creation with separate adult confirmation', () => {
    const html = renderToStaticMarkup(<AuthPanel legacyProfile={false} submit={noop}/>);
    expect(html).toContain('Create account');
    expect(html).toContain('type="submit"');
    expect(html).toContain('autoComplete="username"');
    expect(html).toContain('autoComplete="new-password"');
    expect(html).toContain('Confirm password');
    expect(html).toContain('adult parent or caregiver');
    expect(html).toContain('15–128 characters');
    expect(html).not.toContain('type="email"');
    expect(html).not.toContain('Existing parent PIN');
  });
  it('requires the existing PIN only when attaching an existing learner', () => {
    const html = renderToStaticMarkup(<AuthPanel legacyProfile submit={noop}/>);
    expect(html).toContain('Existing parent PIN · 6 digits');
    expect(html).toContain('Keep the progress already on this browser');
    expect(html).toContain('name="existing-pin"');
  });
  it('uses current-password autofill for sign-in without registration questions', () => {
    const html = renderToStaticMarkup(<AuthPanel initialMode="login" legacyProfile={false} submit={noop}/>);
    expect(html).toContain('autoComplete="current-password"');
    expect(html).not.toContain('Confirm password');
    expect(html).not.toContain('name="existing-pin"');
    expect(html).toContain('No self-service password recovery');
  });
  it('explains record switching before signing into an existing account', () => {
    const html = renderToStaticMarkup(<AuthPanel initialMode="login" legacyProfile submit={noop}/>);
    expect(html).toContain('will not be merged');
    expect(html).toContain('signing in switches learning records');
    expect(html).toContain('type="checkbox"');
  });
  it('provides distinct single-device and all-device sign-out controls and password change', () => {
    const html = renderToStaticMarkup(<AccountPanel username="parent_garden" onLogout={noop} onLogoutAll={noop} onPassword={noop}/>);
    expect(html).toContain('Sign out on this device');
    expect(html).toContain('Sign out on all devices');
    expect(html).toContain('Current password');
    expect(html).toContain('Confirm new password');
    expect(html).toContain('Signing out keeps your saved learning record');
    expect(html).toContain('autoComplete="current-password"');
    expect(html).toContain('autoComplete="new-password"');
  });
  it('renders account names as text, never executable markup', () => {
    const html = renderToStaticMarkup(<AccountPanel username={'<img src=x onerror=alert(1)>'} onLogout={noop} onLogoutAll={noop} onPassword={noop}/>);
    expect(html).toContain('&lt;img');
    expect(html).not.toContain('<img src=x');
    expect(html).not.toContain('<script');
  });
});

describe('client checks complement server authentication', () => {
  it('accepts a parent registration and asks for proof before claiming a guest learner', () => {
    expect(validateRegistration(valid)).toBeNull();
    expect(validateRegistration({ ...valid, legacyProfile: true })).toContain('existing six-digit');
    expect(validateRegistration({ ...valid, legacyProfile: true, pin: '123456' })).toBeNull();
  });
  it('rejects invalid usernames, missing adult confirmation and mismatched passwords', () => {
    expect(validateRegistration({ ...valid, username: 'ab' })).toContain('username');
    expect(validateRegistration({ ...valid, username: 'parent@home' })).toContain('username');
    expect(validateRegistration({ ...valid, adult: false })).toContain('adult');
    expect(validateRegistration({ ...valid, confirmation: 'different' })).toContain('do not match');
  });
  it('counts Unicode characters consistently and rejects passwords outside the allowed length', () => {
    expect(passwordProblem('short')).not.toBeNull();
    expect(passwordProblem('a'.repeat(129))).not.toBeNull();
    expect(passwordProblem('a'.repeat(15))).toBeNull();
    expect(passwordProblem('🌻'.repeat(8))).not.toBeNull();
  });
  it('requires current password and a distinct confirmed replacement', () => {
    expect(validatePasswordChange('', valid.password, valid.password)).toContain('current');
    expect(validatePasswordChange(valid.password, valid.password, valid.password)).toContain('different');
    expect(validatePasswordChange('another old password', valid.password, 'different')).toContain('do not match');
    expect(validatePasswordChange('another old password', valid.password, valid.password)).toBeNull();
  });
});
