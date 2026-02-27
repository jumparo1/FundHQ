# Fund HQ

## About
Centralized dashboard for managing a private investment fund. Deal flow pipeline, research notes, reports, task management, and roadmap. Two co-founders: Jumparo (crypto) & Tihomir (equities).

## Stack
- Single HTML file (`fund-hq.html`, ~147KB)
- Vanilla JS + CSS Custom Properties, dark theme
- Firebase Realtime Database (europe-west1) + localStorage fallback
- Chat assistant "Pamela" for navigation, search, CRUD

## Database
```javascript
DB = {
  deals: [],      // Pipeline: Sourcing → DD → Term Sheet → Closed/Passed
  projects: [],   // Quick project capture
  research: [],   // Structured DD notes (crypto 18-section, stock 10-section)
  reports: [],    // Full research reports
  tasks: []       // Kanban board + milestone roadmap
}
```

## Pages
Dashboard → Deal Flow → Project Dump → Research Notes → Templates → Reports → Tasks → Roadmap → Settings

## Conventions
- `render*()` for pages | `save*()`/`delete*()` for CRUD
- `openModal(type, id)` / `closeModal()` for forms
- `genId()` for unique IDs | `esc(s)` for XSS safety
- Firebase `.on('value')` listeners → `debouncedRender()`
- All records track `editedBy` field

## Scoring
- Overall: 1-10 | Verdict: Strong Buy → Pass | Conviction: High/Medium/Low

---

## Your Fund Knowledge
<!-- Paste your investment thesis, DD frameworks, or fund processes below -->
<!-- Claude will use this context when helping with Fund HQ -->


