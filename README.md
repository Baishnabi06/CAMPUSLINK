# CampusLink

AI-Powered Campus-to-Corporate Placement Management & Analytics Platform.

This repository contains the **base application** (non-AI): authentication,
role-based dashboards, drive management, eligibility filtering, applications,
interview scheduling with conflict detection, offers, document tracking, and
notifications — for three roles: Student, Recruiter, Placement Officer.

AI/ML features (readiness scoring, skill-gap analysis, resume/JD analysis,
candidate matching, predictive analytics) are **not implemented here** by
design. Clean interfaces for them live in `backend/app/services/ai/` for the
AI team to implement independently.

## Features

- JWT authentication with role-based access control (student / recruiter / placement_officer)
- Student: profile, academics, skills, certifications, projects, resume upload
- Recruiter: company profile, full drive CRUD
- Deterministic **Eligibility Filtering** (not AI matching) + application flow
- Interview scheduling with conflict detection (student/venue/panel overlap)
- Offer lifecycle (generate → accept/reject → joining tracking)
- Document submission + officer verification
- In-app notifications across all major workflow events
- Role-specific dashboards + deterministic placement analytics
- Placeholder AI integration layer for future model plug-in

## Architecture

```
Student / Recruiter / Placement Officer (vanilla JS frontend)
                  │
              REST APIs (FastAPI)
                  │
       Auth · Drives · Applications · Interviews
       Offers · Documents · Notifications · Analytics
                  │
               MongoDB
                  │
          AI Integration Layer (interfaces only)
```

## Technology Stack

- **Frontend**: HTML, CSS, vanilla JavaScript (Fetch API) — no framework
- **Backend**: Python, FastAPI
- **Database**: MongoDB (via Motor, async)
- **Auth**: JWT (python-jose), bcrypt password hashing (passlib)

## Folder Structure

See the structure block in this README's accompanying stage notes, or run
`tree` from the project root once created.

## Setup Instructions

### 1. MongoDB

Run MongoDB locally, or create a free cluster at MongoDB Atlas and get its
connection string.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in real values
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

Serve the `frontend/` folder with any static server (e.g. VS Code Live
Server) so relative paths and `localStorage` behave correctly. Do not open
`index.html` directly via `file://`.

### Environment Variables

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB connection string |
| `DATABASE_NAME` | Database name (e.g. `campuslink`) |
| `JWT_SECRET_KEY` | Long random secret for signing JWTs |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |

## User Roles

- **student** — applies to drives, tracks applications/interviews/offers/documents
- **recruiter** — manages company profile, drives, applicants, interviews, offers
- **placement_officer** — oversees students, recruiters, drives, applications, interviews, offers, documents, analytics

## Database Collections

`users`, `students`, `recruiters`, `placement_officers`, `drives`,
`applications`, `interviews`, `offers`, `documents`, `notifications`.

## API Endpoint Summary

| Area | Endpoints |
|---|---|
| Health | `GET /api/health`, `GET /api/health/db` |
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout` |
| Students | `GET/PUT /api/students/me`, `POST /api/students/me/resume` |
| Recruiters | `GET/PUT /api/recruiters/me` |
| Drives | `POST /api/drives`, `GET /api/drives/mine`, `GET /api/drives/open[/id]`, `GET/PUT/DELETE /api/drives/{id}` |
| Applications | `GET .../check-eligibility/{drive_id}`, `POST .../apply/{drive_id}`, `GET .../mine`, `GET .../drive/{drive_id}`, `PATCH .../{id}/status`, `GET .../all` |
| Interviews | `POST /api/interviews`, `GET .../mine`, `GET .../student/mine`, `PUT/PATCH .../{id}`, `GET .../all` |
| Offers | `POST /api/offers`, `GET .../mine`, `PATCH .../{id}/respond`, `GET .../recruiter/mine`, `PATCH .../{id}/status`, `GET .../all` |
| Documents | `POST /api/documents`, `GET .../mine`, `GET .../all`, `PATCH .../{id}/verify` |
| Notifications | `GET /api/notifications/mine`, `GET .../unread-count`, `PATCH .../{id}/read`, `PATCH .../read-all` |
| Analytics | `GET /api/analytics/student/summary`, `.../recruiter/summary`, `.../officer/summary`, `.../officer/placement-stats` |

Full interactive docs are always available at `/docs`.

## AI Integration Points

The AI team implements against these interfaces without needing to modify
existing routes:

- `backend/app/services/ai/readiness_service.py` — readiness scoring
- `backend/app/services/ai/skill_gap_service.py` — skill-gap analysis
- `backend/app/services/ai/matching_service.py` — candidate matching, resume/JD analysis
- `backend/app/services/ai/prediction_service.py` — predictive analytics, recommendations

## Deployment Preparation / Production Checklist

- [ ] Set a strong, unique `JWT_SECRET_KEY` (never reuse the dev value)
- [ ] Use a managed MongoDB (Atlas) connection string, not `localhost`
- [ ] Restrict `CORS_ORIGINS` to the real deployed frontend domain(s) only
- [ ] Serve the backend behind HTTPS (e.g. via a reverse proxy)
- [ ] Turn off `--reload` in production (`uvicorn app.main:app --host 0.0.0.0 --port 8000`)
- [ ] Move file uploads to persistent/cloud storage before scaling beyond one server instance
- [ ] Set appropriate MongoDB user permissions (least privilege, not admin)
- [ ] Add request logging/monitoring before going live
- [ ] Run through the full smoke-test checklist above against the deployed environment