# AGENT STATE

## Current Phase
- Step 0: completed
- Step 1: backend started

## Current Snapshot
- Existing frontend is `Vue 3 + Vite`, but mostly JavaScript, not TypeScript.
- Existing backend is `FastAPI`, but currently uses `sqlmodel`, SQLite, and mostly sync DB access.
- Existing product logic already includes auth, jobs, candidate profile, applications, employer responses, and moderation.
- MVP target remains: align implementation with the requested contract and target architecture.

## Completed
- Inspected current project structure without reading the whole repository.
- Inspected active backend routers:
  - `backend/routes/safety.py`
  - `backend/routes/jobs.py`
  - `backend/routes/profile.py`
- Inspected current frontend API surface:
  - `frontend/src/api/auth.js`
  - `frontend/src/api/jobs.js`
  - `frontend/src/api/profile.js`
- Inspected current data models:
  - `backend/database/models.py`
- Created `docs/api_contract.md` with MVP endpoint contract.
- Pushed pre-change backup point to GitHub:
  - branch: `main`
  - commit: `c5237a8`

## In Progress
- Backend micro-step 4:
  use a hybrid bridge so the new app entrypoint serves the already working legacy MVP routes while migration continues.
  Simplify config dependencies to avoid slow package installation on the current Python runtime.
  Switch the default backend startup path to the new hybrid app and smoke-test key endpoints.
- Frontend micro-step 1:
  strengthen API client, auth bootstrap and route guards around the already working UI.
- Frontend micro-step 2:
  move key client session and communication state into a shared global store with Pinia so auth and chat data are not recreated per page.
- Frontend micro-step 3:
  centralize jobs listing, filters, sorting, and bookmark state in a shared store so the vacancies page becomes a real global workflow instead of a local component-only implementation.
- MVP flow hardening:
  make vacancy publication, applying, and employer-candidate communication work end-to-end from the existing production paths.
  Chat flow updated:
  candidate application no longer unlocks chat immediately;
  employer must approve the chat from responses first;
  employer messages are now embedded inside `employer-dashboard` instead of forcing a separate page.
- Frontend polish pass:
  remove technical wording from the vacancies UI, finish select styling, translate the shared footer to Russian, and harden `/messages` and `/resume-builder` so they work as production-facing screens instead of partial flows.

## Backend Micro-Steps
1. Create target backend app skeleton:
   - `main.py`
   - `core/`
   - `db/`
   - `models/`
   - `schemas/`
   - `routers/`
   - `services/`
2. Configure async database layer:
   - SQLAlchemy 2.0 async engine/session
   - base model setup
   - config loading
   - first Alembic baseline
3. Implement auth module:
   - register
   - login
   - get current user
   - default admin bootstrap
4. Implement jobs module:
   - public jobs
   - employer CRUD
   - moderation approve/reject
5. Implement candidate module:
   - profile get/update
   - apply to job
   - my applications
6. Implement employer responses module:
   - list responses
   - delete response
7. Final backend pass:
   - CORS
   - static uploads
   - response validation
   - smoke test of all routes

## Frontend Micro-Steps
1. Create target frontend skeleton:
   - `src/api/`
   - `src/stores/`
   - `src/router/`
   - `src/views/`
   - `src/components/`
   - `src/types/`
2. Generate TypeScript API types from `docs/api_contract.md`.
3. Implement shared API client:
   - auth token handling
   - typed requests
   - typed error handling
4. Implement auth flow screens:
   - login
   - registration
   - session bootstrap
5. Implement jobs UX:
   - jobs listing
   - job detail
   - candidate apply flow
6. Implement dashboard UX:
   - employer jobs/responses/moderation shortcuts
   - candidate profile/applications
7. Final frontend pass:
   - Pinia stores
   - route guards
   - loading/error states
   - visual QA in browser

## Remaining
- Keep migrating route groups from legacy modules into the new stack incrementally.
- Prioritize working MVP over full architectural replacement in one pass.
- Stabilize frontend auth/session flow before deeper visual and TypeScript migration.
- Verify complete cycle:
  create vacancy -> apply -> open conversation -> exchange messages
- Centralize key frontend state so auth bootstrap, active chat, and message threads are reused across views instead of recreated locally.
- Replace vacancies-page placeholder filters with real, stateful filters backed by shared store data and synced URL parameters.
- Add conversation deletion and live refresh behavior so employer-candidate messaging stays current without manual reloads.
- Verify with a fresh candidate application that a brand-new unapproved response stays out of `/messages` until employer approval, then appears instantly after approval.
- Lock resume builder to authenticated candidates only and complete all three profile steps with real avatar/document uploads.

## Risks / Notes
- Current codebase already contains working pieces. During migration we should replace them incrementally, not blindly rewrite everything at once.
- Because the requested stack differs from the current implementation, Step 1 should prioritize architecture alignment before feature polish.
- Fastest path to MVP: run a hybrid backend where `backend/app/main.py` exposes both the new foundation and the proven legacy business routes.
