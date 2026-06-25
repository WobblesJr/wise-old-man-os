// Shared design tokens + label maps. Single source of truth for colors/labels.

export const ACCENT = { personal: '#34d399', work: '#f59e0b' }

// Action drives the task left color spine.
export const ACTION_SPINE = {
  action: '#ef4444', wait: '#eab308', hold: '#a855f7', read: '#22c55e', event: '#3b82f6',
}
export const ACTION_LABEL = {
  action: 'Action', wait: 'Wait', hold: 'Hold', read: 'Read', event: 'Event',
}

// Status is the secondary dot/label.
export const STATUS = {
  not_started: { label: 'Not started', dot: '#64748b' },
  in_progress: { label: 'In progress', dot: '#38bdf8' },
  completed:   { label: 'Completed',   dot: '#22c55e' },
  delegated:   { label: 'Delegated',   dot: '#a855f7' },
  blocked:     { label: 'Blocked',     dot: '#ef4444' },
}

export const URGENCY = { high: '#ef4444', med: '#eab308', low: '#64748b' }

export const CONN_STATUS = { ok: '#22c55e', mock: '#38bdf8', stubbed: '#eab308', blocked: '#ef4444' }

export const TASK_FILTERS = [
  ['all', 'All'], ['mine', 'Mine'],
  ['action', 'Action'], ['wait', 'Wait'], ['hold', 'Hold'], ['read', 'Read'], ['event', 'Event'],
]

export const fmtTokens = (n) =>
  n >= 1e6 ? (n / 1e6).toFixed(2) + 'M' : n >= 1e3 ? Math.round(n / 1e3) + 'k' : String(n)
