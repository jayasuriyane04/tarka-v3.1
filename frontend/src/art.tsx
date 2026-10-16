import type { ReactNode } from 'react';
type IconName = 'arrow' | 'back' | 'check' | 'close' | 'book' | 'maths' | 'star' | 'shield' | 'leaf' | 'bulb' | 'home' | 'download' | 'lock' | 'settings' | 'heart';
export function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    arrow: <path d="M4 12h16m-6-6 6 6-6 6"/>, back: <path d="M20 12H4m6-6-6 6 6 6"/>,
    check: <path d="m5 12 4 4L19 6"/>, close: <path d="m6 6 12 12M6 18 18 6"/>,
    book: <><path d="M12 5v15M3 4c3-1 6-1 9 1 3-2 6-2 9-1v15c-3-1-6-1-9 1-3-2-6-2-9-1Z"/></>,
    maths: <><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 7h8M8 11h1m6 0h1m-8 4h1m6 0h1m-8 3h1m6 0h1"/></>,
    star: <path d="m12 3 2.8 5.8 6.4.9-4.6 4.5 1.1 6.3-5.7-3-5.7 3 1.1-6.3-4.6-4.5 6.4-.9Z"/>,
    shield: <><path d="m12 3 8 3v6c0 4-5 8-8 9-3-1-8-5-8-9V6Z"/><path d="m8 12 3 3 5-6"/></>,
    leaf: <><path d="M20 3C7 2 2 8 6 15S21 15 20 3ZM4 21 15 9"/></>,
    bulb: <><path d="M9 18h6M10 22h4M8 14a7 7 0 1 1 8 0l-1 4H9Z"/></>,
    home: <><path d="m3 11 9-8 9 8M5 9v12h14V9M9 21v-7h6v7"/></>,
    download: <><path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/></>,
    lock: <><rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/></>,
    settings: <><path d="M4 7h16M4 17h16"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/></>,
    heart: <path d="M20 4c-3-2-6-1-8 2-2-3-5-4-8-2-4 3-1 9 8 16 9-7 12-13 8-16Z"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
export function Brand() { return <span className="brand"><span className="brand-mark" aria-hidden="true">t<span/></span>tarka<span className="brand-period">.</span></span>; }

export function LearningArt({ kind = 'welcome', compact = false }: { kind?: 'welcome' | 'maths' | 'reading'; compact?: boolean }) {
  return <svg className={`learning-art ${compact ? 'compact' : ''}`} viewBox="0 0 440 290" fill="none" aria-hidden="true">
    <ellipse cx="224" cy="252" rx="152" ry="15" fill="#C8C3DA" opacity=".24"/>
    <circle cx="220" cy="136" r="105" fill={kind === 'maths' ? '#D8E9DD' : kind === 'reading' ? '#F2DFCA' : '#E5DEF3'}/>
    <path d="m90 72 4 10 10 4-10 4-4 10-4-10-10-4 10-4Z" fill="#D8B655"/>
    <path d="m352 160 3 8 8 3-8 3-3 8-3-8-8-3 8-3Z" fill="#9789BF"/>
    <circle cx="337" cy="68" r="5" fill="#75A99A"/><circle cx="109" cy="206" r="4" fill="#B7A4D4"/>
    {kind !== 'maths' && <g transform="translate(83 82) rotate(-9 110 76)"><path d="M11 21c36-13 63-5 91 10 28-15 62-21 96-10v112c-37-11-69-4-96 8-27-12-55-19-91-8Z" fill="#FFFDF5" stroke="#455F57" strokeWidth="3" strokeLinejoin="round"/><path d="M102 32v109" stroke="#B6B5A5" strokeWidth="2"/><path d="m28 50 50 7m-50 12 50 7m-50 12 40 6m36-30 50-9m-50 28 50-9m-50 28 39-7" stroke="#A9B7A4" strokeWidth="4" strokeLinecap="round"/><path d="M160 13v43l-12-7-12 10V15" fill="#D78C6D"/></g>}
    {kind !== 'reading' && <g transform={kind === 'maths' ? 'translate(116 64)' : 'translate(259 119) rotate(9 45 50)'}><rect x="0" y="0" width="105" height="128" rx="16" fill="#4B8678"/><rect x="12" y="13" width="81" height="30" rx="6" fill="#D7EBCE"/><path d="M69 24h12m-6-5v10" stroke="#49715A" strokeWidth="3" strokeLinecap="round"/>{[0,1,2].map((row) => [0,1,2].map((column) => <rect key={`${row}-${column}`} x={15+column*27} y={55+row*21} width="20" height="15" rx="4" fill={row===2&&column===2?'#ECCB74':'#B9D4BF'}/>))}</g>}
    <g transform={kind === 'maths' ? 'translate(253 169) rotate(9)' : 'translate(146 204) rotate(-5)'}><rect width="53" height="50" rx="9" fill="#E9C77D"/><path d="M15 25h22m-11-11v22" stroke="#826835" strokeWidth="4" strokeLinecap="round"/></g>
    <path d="M338 225c-4-30 3-45 22-57-1 27-5 42-22 57Z" fill="#91AE85"/><path d="M338 225c-18-23-21-37-14-53 13 16 19 34 14 53Z" fill="#B1C39B"/><path d="M336 222v23" stroke="#6E8F66" strokeWidth="3" strokeLinecap="round"/>
  </svg>;
}
