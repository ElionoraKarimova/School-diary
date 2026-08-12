# School Diary

A Django + Django REST Framework backend for school process automation — a digital gradebook for teachers and a weekly planner (Student Dashboard) for students. It ships both a server-rendered web UI and a JWT-secured REST API, and is packaged for production with Docker, Celery/Redis and CI/CD.

## Features

**Core**
- Role-based access control (Teacher, Student, Admin, Parent) with a custom `User` model
- Grade tracking, per-lesson homework, and a weekly class schedule
- Server-rendered web UI **and** a REST API (pagination, filtering, role-based writes)
- Object-level permissions: a teacher can only edit **their own** grades/homework
- Interactive API docs (Swagger UI via drf-spectacular)

**Production-grade additions**
- **JWT authentication** for API clients, alongside session auth for the web UI
- **Rate limiting / throttling** — global anon/user limits plus a tighter limit on grade writes
- **Database performance** — composite indexes on the hot read paths
- **Aggregation** — an averages endpoint computed in-database with the ORM (`annotate` + `Avg`)
- **Raw SQL + PL/pgSQL** — a `student_average()` PL/pgSQL function called with parameterized SQL
- **Async background tasks** — Celery + Redis; creating a grade queues a notification task
- **Production Docker** — multi-stage, non-root image served by gunicorn + WhiteNoise
- **CI/CD** — GitHub Actions runs black, flake8, mypy and pytest; deploy blueprint for Render
- **Typed codebase** — type hints throughout, checked with mypy

## Tech Stack

Python · Django · Django REST Framework · PostgreSQL (+ PL/pgSQL) · Celery · Redis · Docker / Docker Compose · gunicorn · WhiteNoise · pytest / factory-boy · flake8 / black / mypy · drf-spectacular

## Running the project

1. Clone the repository:
   ```
   git clone https://github.com/ElionoraKarimova/School-diary.git
   cd School-diary
   ```

2. Copy `.env.example` to `.env` and fill in the values:
   ```
   cp .env.example .env
   ```

3. Build and start the containers:
   ```
   docker-compose up --build
   ```

4. The app will be available at `http://localhost:8000`
## The bug I found and fixed (grade ownership)

While hardening the API I found that **newly created grades were saved with `teacher = NULL`**. The `GradeSerializer` didn't expose `teacher`, and the viewset didn't set it on create, so the owning teacher was never recorded. Because the object-level permission checks `grade.teacher == request.user`, this silently broke ownership: the "teacher edits their own grade" path could never actually pass on a real, API-created grade. The existing test masked it by assigning `teacher` directly through the ORM instead of via the API.

**The fix:** `GradeViewSet.perform_create` now stamps `teacher=request.user` from the authenticated user (never from client input), `teacher` is a read-only serializer field, and there is a **positive test** that creates a grade through the API and then edits it as the owning teacher — the exact path that used to fail.

## Using the API (JWT)

```bash
# 1) Obtain a token pair
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<user>", "password": "<pass>"}'

# 2) Call the API with the access token
curl http://localhost:8000/api/v1/grades/ \
  -H "Authorization: Bearer <access-token>"
```

Handy endpoints: `GET /api/v1/grades/averages/` (ORM aggregation) and `GET /api/v1/grades/my-average/` (PL/pgSQL function).

## Logging in / Access points

There are three separate entry points into the app, depending on the role:

- **Teacher / Student login**: `http://localhost:8000/login/`
  This is the main login page for the web interface (schedule, gradebook, diary).

- **Django admin**: `http://localhost:8000/admin/`
  Log in here with a superuser account (created with `python manage.py createsuperuser`).
  From here you can:
  - Create teacher, student, parent, and admin accounts (set the `role` field on the user)
  - Manage groups, subjects, grades, homework, and schedule entries directly
  - Browse the underlying database records for any model

- **Custom Admin Dashboard**: `http://localhost:8000/admin-panel/`
  A dedicated in-app page (separate from Django admin) for users with the `ADMIN` role.
  Lets you add/delete students and schedule entries through a simple UI, without touching Django admin.

- **Interactive API documentation (Swagger UI)**: `http://localhost:8000/api/docs/`
  Lets you browse and test every API endpoint directly from the browser, including sending
  requests and viewing the raw JSON responses.

## Running tests

```
docker compose exec web pytest -v
```

## Code quality

```
docker compose exec web black --check gradebook core users
docker compose exec web flake8 gradebook core users
docker compose exec web mypy gradebook core users --config-file mypy.ini
```

## Main API endpoints

- `/api/v1/grades/` — grades (filterable by `subject`, `student`, `date`; write access restricted to teachers)
- `/api/v1/homeworks/` — homework assignments (filterable by `schedule`, `date`; write access restricted to teachers)
- `/api/v1/schedules/` — read-only class schedule
