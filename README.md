# Migrator

**The Universal Migration CLI for Python Apps**

A lightweight, framework-agnostic database migration tool for Python projects using SQLAlchemy. 
Migrator automates what Alembic requires developers to set up manually — making migrations as simple as Django's `makemigrations` and `migrate`, but flexible enough for any project.

## ✨ Features

- **Zero boilerplate** — one command to init and start migrating
- **Auto-detect models** — finds SQLAlchemy Base classes automatically
- **Smart config** — no need to manually edit alembic.ini or env.py
- **Framework agnostic** — works with FastAPI, Flask, or standalone SQLAlchemy
- **Pythonic CLI** — clean, readable, extensible commands

## 📦 Installation

```bash
# Quick install
curl -sSL https://raw.githubusercontent.com/Adelodunpeter25/migrator/main/install.sh | bash

# Or using pip
pip install migrator-cli

# Or using uv
uv add migrator-cli
```

## 🚀 Quick Start

> **Note:** If you have an existing database with tables, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) first.

### 1. Set up your database URL

Create a `.env` file:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

Or use `settings.py`, `config.py`, `config.yaml`, or `config.toml`.

### 2. Initialize migrations

```bash
migrator init
```

### 3. Create your first migration

```bash
migrator makemigrations "create user table"
```

### 4. Apply migrations

```bash
migrator migrate
```

## 📖 Commands

```bash
# Initialize migration environment
migrator init

# Create new migration
migrator makemigrations "add email to users"

# Apply migrations
migrator migrate

# Rollback migrations
migrator downgrade

# Show migration history
migrator history

# Show current revision
migrator current

# Mark database as migrated (for existing databases)
migrator stamp head

# Show migration status
migrator status
```

## ⚙️ Configuration

Migrator auto-detects your database URL from `.env`, environment variables, `settings.py`, `config.py`, `config.yaml`, or `config.toml`.

```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## 🔧 Troubleshooting

**Existing database with tables?**
```bash
migrator init
migrator makemigrations "initial"
migrator stamp head  # Don't run migrate!
```
See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed instructions.

**Foreign key constraint errors?**  
Use `migrator stamp head` to mark existing database as migrated.

**Missing database driver?**  
PostgreSQL: `psycopg2-binary` is included. For others: `pip install pymysql` (MySQL) or `pip install cx_oracle` (Oracle).

## 🤝 Contributing

Contributions welcome! Submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.