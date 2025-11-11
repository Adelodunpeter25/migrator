# 🧩 Migrator

**The Universal Migration CLI for Python Apps**

A lightweight, framework-agnostic database migration tool for Python projects using SQLAlchemy. Migrator automates what Alembic requires developers to set up manually — making migrations as simple as Django's `makemigrations` and `migrate`, but flexible enough for any project.

## ✨ Features

- 🟢 **Zero boilerplate** — one command to init and start migrating
- ⚙️ **Auto-detect models** — finds SQLAlchemy Base classes automatically
- 🧠 **Smart config** — no need to manually edit alembic.ini or env.py
- 🧰 **Framework agnostic** — works with FastAPI, Flask, or standalone SQLAlchemy
- 🐍 **Pythonic CLI** — clean, readable, extensible commands
- 🪶 **Lightweight** — minimal dependencies
- 🎨 **Beautiful output** — Rich terminal UI with colors and emojis

## 📦 Installation

```bash
pip install migrator
```

Or with uv:

```bash
uv add migrator
```

## 🚀 Quick Start

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

This creates:

```
migrations/
├── versions/
├── env.py
├── script.py.mako
└── alembic.ini
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

### `migrator init`

Initialize migration environment in your project.

```bash
migrator init
migrator init --dir custom_migrations
```

### `migrator makemigrations`

Create a new migration with auto-detection.

```bash
migrator makemigrations "add email to users"
migrator makemigrations "initial" --manual  # Create empty migration
```

### `migrator migrate`

Apply pending migrations.

```bash
migrator migrate
migrator migrate --revision abc123  # Migrate to specific revision
```

### `migrator downgrade`

Rollback migrations.

```bash
migrator downgrade  # Rollback one migration
migrator downgrade --revision abc123  # Rollback to specific revision
migrator downgrade --revision base  # Rollback all migrations
```

### `migrator history`

Show migration history.

```bash
migrator history
```

Output:

```
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Revision    ┃ Message                ┃ Status   ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ abc123def456│ create user table      │ ✅ applied│
│ def789ghi012│ add email to users     │ ⏳ pending│
└─────────────┴────────────────────────┴──────────┘
```

### `migrator current`

Show current database revision.

```bash
migrator current
```

## ⚙️ Configuration

Migrator automatically detects your database URL from multiple sources (in order):

1. `.env` file (`DATABASE_URL` or `SQLALCHEMY_DATABASE_URI`)
2. Environment variables
3. `settings.py` or `config.py`
4. `config.yaml` or `config.toml`

### Example configurations

**.env**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

**settings.py**
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
```

**config.yaml**
```yaml
database:
  url: postgresql://user:password@localhost:5432/dbname
```

**config.toml**
```toml
[database]
url = "postgresql://user:password@localhost:5432/dbname"
```

## 🔧 How It Works

### Auto-Detection

Migrator automatically finds your SQLAlchemy Base class by:

1. Checking common import paths (`app.models`, `models`, `database`, etc.)
2. Scanning your project files for declarative base classes
3. Injecting the correct import into Alembic's `env.py`

### Alembic Integration

Migrator wraps Alembic's powerful migration engine with a simpler interface:

- Uses `alembic.command` API internally
- Customizes templates for auto-import
- Provides Django-style command names
- Adds beautiful terminal output

## 🛠️ Technology Stack

| Component   | Library        | Purpose                    |
|-------------|----------------|----------------------------|
| CLI         | Typer          | Command-line interface     |
| ORM         | SQLAlchemy     | Database models            |
| Migrations  | Alembic        | Migration engine           |
| Config      | python-dotenv  | Environment variables      |
| Output      | Rich           | Terminal UI                |
| Validation  | Pydantic       | Configuration validation   |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [Alembic](https://alembic.sqlalchemy.org/)
- Inspired by Django's migration system
- CLI powered by [Typer](https://typer.tiangolo.com/)
- Beautiful output by [Rich](https://rich.readthedocs.io/)
