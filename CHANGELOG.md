# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-11-11

### Added
- `stamp` command to mark database as migrated without running migrations
- `status` command to show pending migrations and database state
- Pre-migration check for existing tables with interactive prompt
- `--dry-run` flag for migrate command (documentation)
- Better error messages for foreign key constraint failures

### Fixed
- Added `psycopg2-binary` as core dependency for PostgreSQL support
- Improved handling of existing database schemas
- Added helpful tips when migration conflicts occur

## [0.1.0] - 2025-11-11

### Added
- Initial release
- CLI commands: init, makemigrations, migrate, downgrade, history, current
- Auto-detect SQLAlchemy Base classes
- Auto-detect database URL from multiple sources (.env, settings.py, config.py, config.yaml, config.toml)
- Alembic backend integration
- Custom templates with auto-import
- Rich terminal output with colors and emojis
