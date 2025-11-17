# Test App

FastAPI test application for migrator CLI.

## Setup

```bash
cd test-app
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

## Test Migrator

```bash
# Initialize migrations
migrator init

# Create migration
migrator makemigrations "initial tables"

# Apply migrations
migrator migrate
```