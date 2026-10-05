// CampusLink shared icon set — clean, stroke-based SVGs (no external icon
// font/library). Every icon shares a 24x24 viewBox so they drop in at any
// size via CSS. Usage: ICONS.home, ICONS.briefcase, etc. — each is a ready
// <svg> string. Color follows `currentColor`, so just set `color` in CSS.
const ICON_ATTRS = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"';

const ICONS = {
  home: `<svg ${ICON_ATTRS}><path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9a1 1 0 0 0 1 1h3v-6h4v6h3a1 1 0 0 0 1-1v-9"/></svg>`,

  user: `<svg ${ICON_ATTRS}><circle cx="12" cy="8" r="3.2"/><path d="M5 20c0-3.5 3-6 7-6s7 2.5 7 6"/></svg>`,

  briefcase: `<svg ${ICON_ATTRS}><rect x="3" y="8" width="18" height="11" rx="2"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="3" y1="13" x2="21" y2="13"/></svg>`,

  folder: `<svg ${ICON_ATTRS}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/></svg>`,

  mic: `<svg ${ICON_ATTRS}><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="8" y1="22" x2="16" y2="22"/></svg>`,

  gift: `<svg ${ICON_ATTRS}><rect x="4" y="9" width="16" height="11" rx="1"/><line x1="12" y1="9" x2="12" y2="20"/><path d="M4 9h16"/><path d="M12 9c-1.5 0-3-1-3-2.8A2.2 2.2 0 0 1 11.2 4c1.6 0 2.8 2 2.8 5"/><path d="M12 9c1.5 0 3-1 3-2.8A2.2 2.2 0 0 0 12.8 4c-1.6 0-2.8 2-2.8 5"/></svg>`,

  bell: `<svg ${ICON_ATTRS}><path d="M6 10a6 6 0 0 1 12 0c0 4 1.5 5.5 1.5 5.5h-15S6 14 6 10z"/><path d="M10 18a2 2 0 0 0 4 0"/></svg>`,

  sliders: `<svg ${ICON_ATTRS}><line x1="4" y1="6" x2="20" y2="6"/><circle cx="9" cy="6" r="1.8" fill="currentColor"/><line x1="4" y1="12" x2="20" y2="12"/><circle cx="16" cy="12" r="1.8" fill="currentColor"/><line x1="4" y1="18" x2="20" y2="18"/><circle cx="11" cy="18" r="1.8" fill="currentColor"/></svg>`,

  target: `<svg ${ICON_ATTRS}><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>`,

  fileText: `<svg ${ICON_ATTRS}><path d="M7 3h7l4 4v14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v4h4"/><line x1="8.5" y1="13" x2="15" y2="13"/><line x1="8.5" y1="16.5" x2="15" y2="16.5"/></svg>`,

  clock: `<svg ${ICON_ATTRS}><circle cx="12" cy="12" r="8.5"/><polyline points="12,7 12,12 16,14"/></svg>`,

  star: `<svg ${ICON_ATTRS}><polygon points="12,3 14.6,9 21,9.6 16.2,13.9 17.6,20.2 12,16.8 6.4,20.2 7.8,13.9 3,9.6 9.4,9"/></svg>`,

  checkCircle: `<svg ${ICON_ATTRS}><circle cx="12" cy="12" r="8.5"/><polyline points="8,12.3 11,15.3 16,9.3"/></svg>`,

  barChart: `<svg ${ICON_ATTRS}><line x1="5" y1="20" x2="5" y2="12"/><line x1="12" y1="20" x2="12" y2="7"/><line x1="19" y1="20" x2="19" y2="15"/></svg>`,

  trendingUp: `<svg ${ICON_ATTRS}><polyline points="3,17 9,11 13,15 21,7"/><polyline points="15,7 21,7 21,13"/></svg>`,

  building: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="5" y="2" width="14" height="20" rx="1"/><rect x="8" y="6" width="2" height="2" fill="currentColor" stroke="none"/><rect x="14" y="6" width="2" height="2" fill="currentColor" stroke="none"/><rect x="8" y="11" width="2" height="2" fill="currentColor" stroke="none"/><rect x="14" y="11" width="2" height="2" fill="currentColor" stroke="none"/><rect x="8" y="16" width="2" height="2" fill="currentColor" stroke="none"/><rect x="14" y="16" width="2" height="2" fill="currentColor" stroke="none"/></svg>`,

  users: `<svg ${ICON_ATTRS}><circle cx="9" cy="8" r="3"/><path d="M3 20c0-3 2.5-5 6-5s6 2 6 5"/><circle cx="17" cy="9" r="2.5"/><path d="M15.2 20c.3-2.2 1.8-3.8 4-4.3"/></svg>`,

  graduationCap: `<svg ${ICON_ATTRS}><path d="M12 3 2 8l10 5 10-5-10-5z"/><path d="M6 10.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-5.5"/><line x1="22" y1="8" x2="22" y2="14"/></svg>`,

  activity: `<svg ${ICON_ATTRS}><polyline points="3,12 8,12 10,7 14,17 16,12 21,12"/></svg>`,

  search: `<svg ${ICON_ATTRS}><circle cx="10" cy="10" r="6"/><line x1="14.5" y1="14.5" x2="20" y2="20"/></svg>`,

  arrowRight: `<svg ${ICON_ATTRS}><line x1="5" y1="12" x2="19" y2="12"/><polyline points="13,6 19,12 13,18"/></svg>`,

  mapPin: `<svg ${ICON_ATTRS}><path d="M12 21s7-7.5 7-12a7 7 0 1 0-14 0c0 4.5 7 12 7 12z"/><circle cx="12" cy="9" r="2.3"/></svg>`,

  wallet: `<svg ${ICON_ATTRS}><rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18"/><circle cx="16.5" cy="14" r="1.1" fill="currentColor" stroke="none"/></svg>`,
};

// Small helper: wraps an icon string in a sized span so call sites don't
// repeat inline styles. size in px, defaults to 18.
function iconSpan(name, size) {
  const svg = ICONS[name] || "";
  return `<span class="icon" style="width:${size || 18}px;height:${size || 18}px;display:inline-flex">${svg}</span>`;
}