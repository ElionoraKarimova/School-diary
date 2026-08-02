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

5. Interactive API documentation (Swagger): `http://localhost:8000/api/docs/`

6. To access the admin dashboard, create a user with the `ADMIN` role via Django admin (`http://localhost:8000/admin/`), then log in and visit `http://localhost:8000/admin-panel/`

7. Teachers and students log in at `http://localhost:8000/login/`. You can create teacher/student accounts via Django admin (`http://localhost:8000/admin/`), setting the `role` field accordingly.

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