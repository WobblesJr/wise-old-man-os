// Thin API client. Talks to the FastAPI backend; everything is mock-backed there.
const BASE = import.meta.env.VITE_API_BASE || '' // '' => same origin / vite proxy

async function jget(path) {
  const r = await fetch(BASE + path, { headers: { Accept: 'application/json' } })
  if (!r.ok) throw new Error(`${path} -> ${r.status}`)
  return r.json()
}
async function jpost(path, body) {
  const r = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!r.ok) throw new Error(`${path} -> ${r.status}`)
  return r.json()
}
async function jpatch(path, body) {
  const r = await fetch(BASE + path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`${path} -> ${r.status}`)
  return r.json()
}

export const api = {
  health: () => jget('/api/health'),
  dashboard: (scope) => jget(`/api/dashboard?scope=${scope}`),
  cockpit: () => jget('/api/cockpit'),
  tasks: (scope, filter = 'all') => jget(`/api/tasks?scope=${scope}&filter=${filter}`),
  addTask: (payload) => jpost('/api/tasks', payload),
  patchTask: (id, scope, patch) => jpatch(`/api/tasks/${id}?scope=${scope}`, patch),
  approvals: (scope) => jget(`/api/approvals?scope=${scope}`),
  draft: (id) => jget(`/api/drafts/${id}`),
  decide: (approval_id, decision) => jpost('/api/approvals/decide', { approval_id, decision }),
  capture: (payload) => jpost('/api/capture', payload),
  usage: () => jget('/api/usage'),
  runSuggestion: (ref, scope) => jpost(`/api/actions/run/${ref}?scope=${scope}`),
}
