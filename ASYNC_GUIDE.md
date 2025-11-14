# Using Migrator with Async SQLAlchemy

## Overview

Migrator works with async SQLAlchemy projects by automatically converting async database URLs to sync equivalents for Alembic.

## Setup

### 1. Your Async Application

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
```

### 2. Initialize Migrations

```bash
# Migrator will detect and convert the async URL
migrator init --base app.core.database:Base
```

### 3. Create Migrations

```bash
migrator makemigrations "create users table"
```

### 4. Apply Migrations

```bash
migrator migrate
```

## How It Works

- Your app uses `postgresql+asyncpg://` with asyncpg driver
- Migrator converts to `postgresql://` for Alembic (uses psycopg2)
- Both drivers can coexist - no conflicts
- Migrations run during deployment, not in request path

## Supported Async Drivers

| Async Driver | Converted To | Database |
|--------------|--------------|----------|
| +asyncpg | (default) | PostgreSQL |
| +aiomysql | +pymysql | MySQL |
| +aiosqlite | (default) | SQLite |

## Common Issues

### "No module named 'asyncpg'"

This is fine! Migrator uses psycopg2 for migrations. Your app still uses asyncpg.

### "Could not find Base"

Use the --base flag:

```bash
migrator init --base app.core.database:Base
```

### "Database URL not found"

Ensure your .env file is in the project root or parent directory:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

## Example Project Structure

```
backend/
├── app/
│   ├── core/
│   │   └── database.py  # Base = declarative_base()
│   └── models/
│       ├── user.py
│       └── post.py
├── migrations/  # Created by migrator
├── .env  # DATABASE_URL here
└── main.py
```

## Complete Workflow

```bash
# 1. Set up .env
echo "DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db" > .env

# 2. Initialize
migrator init --base app.core.database:Base

# 3. Create migration
migrator makemigrations "initial schema"

# 4. Apply
migrator migrate

# 5. Check status
migrator status
```
