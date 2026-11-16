"""
modules/scaffolder.py
─────────────────────
Pre-built project scaffolding templates for common application types.

When Gemini calls `scaffold_project(project_type, project_name)`, this module
creates the base directory structure and boilerplate files so Gemini only needs
to fill in the application-specific logic.

Supported project types:
  - fastapi          → Python FastAPI REST API
  - react            → React + Vite + TailwindCSS SPA
  - nextjs           → Next.js 14 App Router
  - node-express     → Node.js + Express REST API
  - flutter          → Flutter mobile app
  - django           → Django web application
  - cli-python       → Python CLI tool with Click
  - fullstack-react-fastapi → React frontend + FastAPI backend (monorepo)
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Template Definitions ──────────────────────────────────────────────────────

TEMPLATES = {
    "fastapi": {
        "description": "Python FastAPI REST API with SQLAlchemy, Pydantic, and Alembic",
        "files": {
            "README.md": lambda n: f"""# {n}

A production-ready REST API built with FastAPI.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs
""",
            "requirements.txt": lambda n: """fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy>=2.0.0
alembic>=1.13.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
""",
            ".env.example": lambda n: f"""# Application Settings
APP_NAME={n}
APP_ENV=development
DEBUG=true
SECRET_KEY=change-this-to-a-random-secret-key

# Database
DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgresql://user:password@localhost:5432/{n.lower().replace('-','_')}

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
""",
            ".gitignore": lambda n: """__pycache__/
*.pyc
*.pyo
.env
venv/
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
*.db
""",
            "app/__init__.py": lambda n: "",
            "app/main.py": lambda n: f'''"""
{n} - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {{"status": "ok", "service": settings.APP_NAME}}
''',
            "app/core/__init__.py": lambda n: "",
            "app/core/config.py": lambda n: '''"""Application configuration using Pydantic Settings."""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "My FastAPI App"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "sqlite:///./app.db"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
''',
            "app/api/__init__.py": lambda n: "",
            "app/api/v1/__init__.py": lambda n: "",
            "app/api/v1/router.py": lambda n: '''"""API v1 Router — register all endpoint routers here."""
from fastapi import APIRouter
# from app.api.v1.endpoints import items  # Example import

api_router = APIRouter()
# api_router.include_router(items.router, prefix="/items", tags=["items"])
''',
            "app/models/__init__.py": lambda n: "",
            "app/schemas/__init__.py": lambda n: "",
            "tests/__init__.py": lambda n: "",
            "tests/test_main.py": lambda n: '''"""Basic health check test."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
''',
        },
    },

    "react": {
        "description": "React + Vite + TypeScript + TailwindCSS SPA",
        "files": {
            "README.md": lambda n: f"""# {n}

A modern React SPA built with Vite, TypeScript, and TailwindCSS.

## Setup

```bash
npm install
cp .env.example .env.local
```

## Run

```bash
npm run dev
```

Open: http://localhost:5173
""",
            "package.json": lambda n: f'''{{"name": "{n.lower().replace(' ', '-')}", "version": "0.1.0", "private": true, "scripts": {{"dev": "vite", "build": "tsc && vite build", "preview": "vite preview", "lint": "eslint src --ext ts,tsx"}}, "dependencies": {{"react": "^18.3.0", "react-dom": "^18.3.0", "react-router-dom": "^6.23.0", "axios": "^1.7.0"}}, "devDependencies": {{"@types/react": "^18.3.0", "@types/react-dom": "^18.3.0", "@vitejs/plugin-react": "^4.3.0", "autoprefixer": "^10.4.19", "eslint": "^9.0.0", "postcss": "^8.4.38", "tailwindcss": "^3.4.4", "typescript": "^5.4.5", "vite": "^5.2.11"}}}}''',
            ".env.example": lambda n: f"""VITE_APP_NAME={n}
VITE_API_BASE_URL=http://localhost:8000/api/v1
""",
            ".gitignore": lambda n: """node_modules/
dist/
.env.local
.env.*.local
*.log
.DS_Store
""",
            "index.html": lambda n: f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{n}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",
            "src/main.tsx": lambda n: """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
            "src/App.tsx": lambda n: f"""import React from 'react'

function App() {{
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">{n}</h1>
        <p className="text-gray-600">Your app is ready. Start building!</p>
      </div>
    </div>
  )
}}

export default App
""",
            "src/index.css": lambda n: """@tailwind base;
@tailwind components;
@tailwind utilities;
""",
        },
    },

    "node-express": {
        "description": "Node.js + Express REST API with TypeScript",
        "files": {
            "README.md": lambda n: f"""# {n}

A Node.js REST API built with Express and TypeScript.

## Setup

```bash
npm install
cp .env.example .env
```

## Run

```bash
npm run dev    # Development with hot reload
npm run build  # Build for production
npm start      # Run production build
```
""",
            "package.json": lambda n: f'''{{"name": "{n.lower().replace(' ', '-')}", "version": "1.0.0", "scripts": {{"dev": "ts-node-dev --respawn src/index.ts", "build": "tsc", "start": "node dist/index.js", "lint": "eslint src --ext .ts"}}, "dependencies": {{"express": "^4.19.0", "cors": "^2.8.5", "dotenv": "^16.4.5", "helmet": "^7.1.0", "morgan": "^1.10.0"}}, "devDependencies": {{"@types/cors": "^2.8.17", "@types/express": "^4.17.21", "@types/morgan": "^1.9.9", "@types/node": "^20.14.0", "ts-node-dev": "^2.0.0", "typescript": "^5.4.5"}}}}''',
            ".env.example": lambda n: f"""NODE_ENV=development
PORT=3000
APP_NAME={n}
JWT_SECRET=change-this-to-a-random-secret
DATABASE_URL=
""",
            ".gitignore": lambda n: """node_modules/
dist/
.env
*.log
""",
            "src/index.ts": lambda n: f'''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Health check
app.get('/health', (_req, res) => {{
  res.json({{ status: 'ok', service: '{n}' }});
}});

// TODO: Add your routes here
// import {{ router }} from './routes/example';
// app.use('/api/v1/example', router);

app.listen(PORT, () => {{
  console.log(`🚀 {n} running on http://localhost:${{PORT}}`);
}});

export default app;
''',
            "tsconfig.json": lambda n: """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
""",
        },
    },

    "cli-python": {
        "description": "Python CLI tool with Click, rich output, and packaging",
        "files": {
            "README.md": lambda n: f"""# {n}

A Python CLI tool.

## Install (development)

```bash
pip install -e .
```

## Usage

```bash
{n.lower().replace(' ', '-')} --help
```
""",
            "setup.py": lambda n: f"""from setuptools import setup, find_packages

setup(
    name="{n.lower().replace(' ', '-')}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    entry_points={{
        "console_scripts": [
            "{n.lower().replace(' ', '-')}=src.cli:main",
        ],
    }},
)
""",
            "requirements.txt": lambda n: """click>=8.1.0
rich>=13.0.0
python-dotenv>=1.0.0
""",
            ".gitignore": lambda n: """__pycache__/
*.pyc
.env
venv/
*.egg-info/
dist/
build/
""",
            "src/__init__.py": lambda n: "",
            "src/cli.py": lambda n: f'''"""
{n} — CLI Entry Point
"""
import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """{n} CLI tool."""
    pass


@main.command()
@click.argument("name", default="World")
def hello(name: str):
    """Say hello."""
    console.print(Panel(f"[bold green]Hello, {{name}}![/bold green]", title="{n}"))


if __name__ == "__main__":
    main()
''',
        },
    },

    "fullstack-react-fastapi": {
        "description": "Full-stack monorepo: React frontend + FastAPI backend",
        "files": {
            "README.md": lambda n: f"""# {n} — Full-Stack Application

## Structure

```
{n}/
├── backend/    # FastAPI REST API
└── frontend/   # React + Vite + TailwindCSS
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:5173
""",
            "docker-compose.yml": lambda n: f"""version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
""",
            ".gitignore": lambda n: """# Python
__pycache__/
*.pyc
.env
venv/
*.db

# Node
node_modules/
dist/
.env.local
*.log
""",
        },
    },
}


def scaffold_project(project_type: str, project_name: str) -> str:
    """
    Scaffold a standard project template.

    Args:
        project_type: Type of project (see TEMPLATES keys).
        project_name: Name of the project (used as root directory).

    Returns:
        Success message describing what was created.
    """
    if project_type not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(
            f"Unknown project type: '{project_type}'. "
            f"Available types: {available}"
        )

    template = TEMPLATES[project_type]
    root = Path(project_name)
    root.mkdir(parents=True, exist_ok=True)

    created_files = []

    for rel_path, content_fn in template["files"].items():
        file_path = root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = content_fn(project_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        created_files.append(str(file_path))
        logger.info(f"Scaffolded: {file_path}")

    summary = (
        f"✅ Scaffolded '{project_type}' project: '{project_name}'\n"
        f"   Description: {template['description']}\n"
        f"   Files created ({len(created_files)}):\n"
        + "\n".join(f"   - {f}" for f in created_files)
    )

    return summary
