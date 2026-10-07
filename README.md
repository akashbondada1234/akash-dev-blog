# Akash Bondada — Developer blog

## Live website

🌐 **[Open Akash's Engineering Journal](https://bondada-akash-blog.netlify.app/)**

[![Live Blog](https://img.shields.io/badge/Live_Blog-Open_site-2563eb?style=for-the-badge)](https://bondada-akash-blog.netlify.app/)

Premium developer portfolio and technical blog for Akash Bondada, built with React/Vite/Tailwind and FastAPI/SQLAlchemy/SQLite.

## Run locally

### Backend

```bash
cd backend
python -m venv env
# Windows: env\Scripts\activate   |   macOS/Linux: source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000` and seeds sample content on first start.
For local development, the seed admin is `admin@akash.dev` / `password123`. Before deployment, set `ENVIRONMENT=production`, a strong `SECRET_KEY`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` in the hosting provider. Never commit these values.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`. Set `VITE_API_URL` to point at another API host.

## Structure

`backend/` contains the FastAPI app, models, JWT helpers, routes, image uploads, and seed data. `frontend/src/` contains reusable components, pages, API services, and auth/theme state. SQLite is used by default; set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL for deployment.

## API

Interactive docs are available at `/docs`. Public endpoints include `GET /posts`, `GET /posts/{slug}`, and `GET /categories`. Admin endpoints require `Authorization: Bearer <token>`.
