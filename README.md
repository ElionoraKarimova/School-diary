# School Diary

A Django + Django REST Framework backend for school process automation — featuring a digital gradebook for teachers and a user-friendly weekly planner (Student Dashboard) for students.

The project is fully containerized with Docker and exposes both a web UI and a REST API ready for integration with mobile apps and third-party services.

## Features

- Role-based access control (Teacher, Student, Admin, Parent)
- Grade tracking on a 0–10 scale
- Homework assignment tracking per lesson
- Admin dashboard for managing students and the class schedule (add/delete)
- REST API with pagination, filtering and role-based write permissions
- Object-level permissions (a teacher can only edit their own grades/homework)
- Interactive API documentation (Swagger UI)
- Automated tests (pytest) and CI (GitHub Actions)

## Tech Stack

- Python, Django, Django REST Framework
- PostgreSQL
- Docker / Docker Compose
- pytest / pytest-django
- drf-spectacular (API docs)
- flake8 / black (code style)

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

## Code style

```
docker compose exec web flake8 .
docker compose exec web black --check .
```

## Main API endpoints

- `/api/v1/grades/` — grades (filterable by `subject`, `student`, `date`; write access restricted to teachers)
- `/api/v1/homeworks/` — homework assignments (filterable by `schedule`, `date`; write access restricted to teachers)
- `/api/v1/schedules/` — read-only class schedule
