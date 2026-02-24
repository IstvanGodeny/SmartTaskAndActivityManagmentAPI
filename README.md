```markdown
> Backend portfolio project by Istvan – Junior Python Developer
```

# Smart Task Manager API

A production-style FastAPI backend application featuring JWT authentication, task ownership validation, database migrations, and full test coverage.

This project is part of my backend portfolio, built with production-ready structure and best practices.

---

## 🚀 Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Alembic (Migrations)
- JWT Authentication
- Pytest
- Poetry
- Docker (optional)

---

## 🔐 Features

- User registration & authentication
- JWT-based login
- Protected endpoints
- Task CRUD operations
- Task ownership validation
- Filtering & query parameters
- Database migrations with Alembic
- Isolated test database
- Automated tests with Pytest

---

## 🏗 Architecture

The project follows a layered architecture:

- API layer (routers)
- Service layer (business logic)
- Data layer (SQLAlchemy models)
- Core configuration & security

---

## 🧪 Testing

```bash
poetry run pytest
```

Includes:
- Auth tests
- Task CRUD tests
- Ownership security tests
- Filtering tests

---

## ⚙️ Installation

```bash
git clone "https://github.com/IstvanGodeny/SmartTaskAndActivityManagmentAPI.git"
cd SmartTaskAndActivityManagmentAPI
poetry install
```
Create your environment file:
```bash
cp .env.example .env
```
Run migrations:
```bash
alembic upgrade head
```
Start development server:
```bash
uvicorn app.main:app --reload
```

---

## 📌 API Documentation

After starting the server:
```bash
http://localhost:8000/docs
```

---

## 🎯 Project Purpose

This project demonstrates:
- Clean architecture
- Secure authentication
- Proper test isolation
- Migration workflow
- Backend best practices

Built as a flagship backend project to demonstrate readiness for Junior Backend / Python Developer roles.

