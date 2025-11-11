# Release Notes - Migrator v0.2.0

## 🎉 What's New

Version 0.2.0 addresses critical feedback from production testing and adds essential features for working with existing databases.

## ✨ New Features

### 1. `stamp` Command
Mark your database as migrated without running migrations - essential for existing databases.

```bash
migrator stamp head  # Mark as latest revision
migrator stamp abc123  # Mark to specific revision
```

**Use Case**: Adding Migrator to a project with an existing database schema.

### 2. `status` Command
Get a comprehensive view of your migration state.

```bash
migrator status
```

**Output**:
- Current revision
- Number of existing tables
- Pending migrations count
- List of pending migrations

### 3. Existing Database Detection
Migrator now automatically detects existing tables and prompts you with options:

```
⚠️  Found 15 existing tables in database

Options:
  1. Mark database as migrated (stamp) - Recommended
  2. Continue anyway (may cause conflicts)
  3. Cancel

Choice [3]:
```

### 4. `--dry-run` Flag
Preview migrations before applying (documentation mode).

```bash
migrator migrate --dry-run
```

### 5. Enhanced Error Messages
Better error handling with helpful tips:

```
❌ Migration failed: foreign key constraint...

💡 Tip: Use 'migrator stamp head' to mark existing database as migrated
```

## 🐛 Bug Fixes

### PostgreSQL Support
- Added `psycopg2-binary` as a core dependency
- No more "No module named 'psycopg2'" errors

### Existing Schema Handling
- Improved detection of existing tables
- Interactive prompts prevent accidental data loss
- Filters out `alembic_version` table from checks

## 📚 Documentation

### New Guides
- **MIGRATION_GUIDE.md**: Comprehensive guide for existing databases
- **Troubleshooting Section**: Common issues and solutions in README

### Updated README
- Documented new `stamp` and `status` commands
- Added existing database workflow
- Troubleshooting section with common scenarios

## 🔄 Migration Path

### From v0.1.0 to v0.2.0

No breaking changes! Simply update:

```bash
pip install --upgrade migrator-cli
```

All existing migrations remain compatible.

## 📊 Test Coverage

- **37 tests passing** ✅
- New tests for `stamp` and `status` commands
- E2E tests updated for existing database scenarios

## 🎯 Addressed Feedback

This release directly addresses feedback from production testing:

| Issue | Status | Solution |
|-------|--------|----------|
| Existing database conflicts | ✅ Fixed | Interactive prompt + stamp command |
| Missing psycopg2 | ✅ Fixed | Added to dependencies |
| No migration status view | ✅ Fixed | New `status` command |
| Poor error messages | ✅ Fixed | Enhanced with helpful tips |
| Need dry-run mode | ✅ Added | `--dry-run` flag |

## 🚀 Quick Start for Existing Databases

```bash
# 1. Initialize
migrator init

# 2. Create initial migration
migrator makemigrations "initial schema"

# 3. Stamp database (don't run migrations!)
migrator stamp head

# 4. Verify
migrator status

# 5. Make changes and migrate normally
migrator makemigrations "add new field"
migrator migrate
```

## 🔮 What's Next (v0.3.0)

- Migration squashing
- Better diff visualization
- Optional database driver dependencies
- Performance optimizations

## 🙏 Credits

Special thanks to the Church Management System team for comprehensive testing and feedback that made this release possible.

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

**Download**: `pip install migrator-cli==0.2.0`

**Documentation**: [README.md](README.md)

**Migration Guide**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
