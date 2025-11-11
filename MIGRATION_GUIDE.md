# Migration Guide for Existing Databases

This guide helps you add Migrator to projects with existing database schemas.

## Scenario 1: Existing Database with Tables

If you have a database that already has tables (e.g., migrating from another ORM or framework):

### Step 1: Initialize Migrator

```bash
migrator init
```

This creates the `migrations/` directory structure.

### Step 2: Create Initial Migration

```bash
migrator makemigrations "initial schema"
```

This generates a migration file reflecting your current SQLAlchemy models.

### Step 3: Stamp the Database

**Important:** Don't run `migrator migrate` yet! Your database already has the tables.

Instead, mark the database as already migrated:

```bash
migrator stamp head
```

This tells Migrator: "The database is already at this revision, don't try to create tables."

### Step 4: Verify

```bash
migrator status
```

You should see:
- Current revision: [your revision]
- Pending migrations: 0

### Step 5: Future Changes

Now you can make changes normally:

```bash
# Modify your models
# Then create migration
migrator makemigrations "add email to users"

# Apply it
migrator migrate
```

## Scenario 2: Migrating from Alembic

If you're already using Alembic directly:

### Option A: Keep Existing Migrations

```bash
# Your existing migrations/ folder stays
# Just start using migrator commands
migrator makemigrations "new feature"
migrator migrate
```

Migrator is compatible with existing Alembic migrations.

### Option B: Fresh Start

```bash
# Backup your database first!

# Remove old migrations
rm -rf migrations/

# Initialize with migrator
migrator init

# Create initial migration
migrator makemigrations "initial schema"

# Stamp database (don't run migrations)
migrator stamp head
```

## Scenario 3: Foreign Key Constraint Errors

If you see errors like:

```
cannot drop table X because other objects depend on it
DETAIL: constraint Y on table Z depends on table X
```

This means you tried to run migrations on an existing database.

### Solution:

```bash
# Check current state
migrator status

# If you see existing tables but no current revision:
migrator stamp head

# This marks the database as migrated without running migrations
```

## Scenario 4: Partial Migration

If some tables exist but not all:

### Manual Approach:

1. Check what exists:
```bash
migrator status
```

2. Edit the generated migration file to skip existing tables:
```python
def upgrade():
    # Comment out tables that already exist
    # op.create_table('existing_table', ...)  # Skip this
    
    # Keep new tables
    op.create_table('new_table', ...)
```

3. Run migration:
```bash
migrator migrate
```

### Recommended Approach:

Create separate migrations for new tables only:

```bash
# Create migration with only new models
migrator makemigrations "add new tables" --manual

# Edit the migration file to add only new tables
# Then apply
migrator migrate
```

## Best Practices

### 1. Always Backup First

```bash
# PostgreSQL
pg_dump dbname > backup.sql

# MySQL
mysqldump dbname > backup.sql

# SQLite
cp database.db database.db.backup
```

### 2. Test in Development First

```bash
# Use a copy of production database
DATABASE_URL=postgresql://localhost/dev_db migrator migrate
```

### 3. Use Status Command

```bash
# Before any operation, check status
migrator status
```

### 4. Stamp Before First Migration

For existing databases, always stamp first:

```bash
migrator init
migrator makemigrations "initial"
migrator stamp head  # Don't forget this!
```

## Common Mistakes

### ❌ Running migrate on existing database

```bash
migrator init
migrator makemigrations "initial"
migrator migrate  # ERROR: Tables already exist!
```

### ✅ Correct approach

```bash
migrator init
migrator makemigrations "initial"
migrator stamp head  # Mark as migrated
migrator status      # Verify
```

## Troubleshooting

### "Table already exists"

```bash
# Solution: Stamp the database
migrator stamp head
```

### "Foreign key constraint fails"

```bash
# Solution: Stamp the database
migrator stamp head
```

### "No such table: alembic_version"

This is normal for new databases. Just run:

```bash
migrator migrate
```

### "Can't locate revision"

```bash
# Check migration history
migrator history

# Stamp to specific revision
migrator stamp abc123
```

## Getting Help

If you encounter issues:

1. Check status: `migrator status`
2. Check history: `migrator history`
3. Check current: `migrator current`
4. Review this guide
5. Open an issue on GitHub

## Example: Real-World Migration

Here's a complete example of adding Migrator to an existing FastAPI project:

```bash
# 1. Install migrator
pip install migrator-cli

# 2. Verify database has tables
psql -d mydb -c "\dt"  # Shows existing tables

# 3. Initialize
migrator init

# 4. Create initial migration
migrator makemigrations "initial schema from existing db"

# 5. DON'T RUN MIGRATE! Instead, stamp:
migrator stamp head

# 6. Verify
migrator status
# Output:
# Current revision: abc123def456
# Existing tables: 15
# Pending migrations: 0

# 7. Now make a change to your models
# Add a new field to User model

# 8. Create migration for the change
migrator makemigrations "add user avatar field"

# 9. Apply the change
migrator migrate

# 10. Verify
migrator status
# Output:
# Current revision: xyz789abc012
# Existing tables: 15
# Pending migrations: 0
```

Success! You've migrated an existing database to Migrator.
