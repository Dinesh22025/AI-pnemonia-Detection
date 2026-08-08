th# PneumoVision AI - Docker Deployment Fix

## New Issue: Registration fails with "network error" on /signup

**Root cause:** `bcrypt==5.0.0` is incompatible with `passlib==1.7.4`. At runtime passlib
tries to read `bcrypt.__about__.__version__` which was removed in bcrypt 4.1+ →
`AttributeError`, which breaks all password hashing. This caused registration to return
HTTP 500, which the frontend displayed as "network error".

**Fix:** Pinned `bcrypt<4.1` in `backend/requirements.txt` so passlib works. Rebuilding
the backend image (ML layers cached, only small packages reinstalled) and recreating the
container.

- [x] Pin bcrypt<4.1 in requirements.txt (done)
- [x] Rebuild backend image (docker-backend:latest)
- [x] Recreate/restart backend container (now running bcrypt 4.0.1)
- [x] Verify /auth/register returns 201 (not 500) — confirmed HTTP 201 + JWT tokens
- [x] Confirm password hashing/verification works (HASH OK / VERIFY OK: True)
- [x] Verify /auth/login returns 200 for registered user (confirmed)
- [x] Confirm signup works end-to-end (POST /auth/register → 201 + JWT)

## Status: ✅ COMPLETE (original deploy)

## Task List

- [x] 1. Restart Docker Desktop engine and verify `docker info` responds
- [x] 2. Fix frontend build: add `output: 'standalone'` + TS/ESLint build guards to `next.config.js`; change `Dockerfile.frontend` to `npm ci`
- [x] 3. Fix backend build: remove `COPY .env .`; copy `deep_learning/` to `/deep_learning/`
- [x] 4. Enable PostgreSQL: `connection.py` reads `DATABASE_URL` from env (SQLite fallback)
- [x] 5. Fix `docker-compose.yml`: remove init-db.sql mount, fix volume targets (/uploads, /static, /logs, /reports), add MODEL_PATH/UPLOAD_DIR env
- [x] 6. Create `docker/ssl/` placeholder directory
- [x] 7. Fix `nginx.conf`: remove `try_files` in `location /` + reload command
- [x] 8. Add root `.dockerignore`
- [x] 9. Build & deploy: `docker compose up --build -d`
- [x] 10. Verify all services healthy (frontend:3000, backend:8000/docs, nginx:80)

## Additional Fixes Applied During Deployment

- **Frontend health check**: `wget --spider` not available in alpine node image → replaced with `node -e` HTTP GET
  against `127.0.0.1:3000`
- **Frontend HOSTNAME=0.0.0.0**: Next.js standalone server was binding only to container IP, causing
  health check ECONNREFUSED → forced 0.0.0.0 binding so it listens on all interfaces
- **requirements-ml.txt**: created to isolate TensorFlow/ML deps with a retry loop in the Dockerfile
  to handle network instability during the large (572MB) wheel download
- **React error #31 on /signup & /login**: FastAPI returns 422 validation errors as an array of
  objects in `detail`. Fixed in BOTH places:
  1. `frontend/services/api.ts` — the shared Axios response interceptor passed the raw `detail`
     array to `toast.error()` on every request → THIS was the root cause of error #31
     (React renders the array of `{type, loc, msg, input, ctx}` objects as a child).
     Now coerces `detail` into a readable string message.
  2. `frontend/pages/signup.tsx` & `login.tsx` — catch blocks also safely extract the message.
  Frontend container rebuilt and redeployed.

## Deployment Summary

All 5 containers are running and healthy:
- `pneumovision-db` (PostgreSQL 15) — healthy, port 5432
- `pneumovision-redis` (Redis 7) — healthy, port 6379
- `pneumovision-backend` (FastAPI) — healthy, port 8000
- `pneumovision-frontend` (Next.js 14 standalone) — healthy, port 3000
- `pneumovision-nginx` (reverse proxy) — running, ports 80/443

Verified:
- Frontend http://localhost:3000 → 200
- Nginx http://localhost → 200
- Backend health http://localhost:8000/health → 200 (database connected, model loaded)
- API docs http://localhost:8000/docs → 200

## Deployed Stack

```bash
docker compose -f docker/docker-compose.yml up --build -d
