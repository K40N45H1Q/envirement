# AGENT STATE

## Current Phase
- Step 0: completed
- Step 1: ready to start after backup push

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

## In Progress
- Create pre-backend backup point in git before structural changes.

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
- Push current state to GitHub
- Start Backend Step 1 micro-step 1

## Risks / Notes
- Current codebase already contains working pieces. During migration we should replace them incrementally, not blindly rewrite everything at once.
- Because the requested stack differs from the current implementation, Step 1 should prioritize architecture alignment before feature polish.
