# Implementation Plan - Migrator v0.2.1

## Overview
Address all feedback from Invoice Generator API testing to support nested project structures, async SQLAlchemy, and improve error reporting.

---

## Phase 1: Configuration Discovery Improvements

### 1.1 Multi-Directory .env Search
**File**: `src/migrator/utils/config_loader.py`

**Current Issue**: Only loads `.env` from current directory
**Solution**: Search up directory tree for `.env` file

```python
@staticmethod
def _find_env_file() -> Optional[Path]:
    """Search for .env file in current and parent directories"""
    current = Path.cwd()
    for _ in range(5):  # Search up 5 levels
        env_file = current / ".env"
        if env_file.exists():
            return env_file
        current = current.parent
    return None

@staticmethod
def load_database_url() -> str:
    """Auto-detect database URL from multiple sources"""
    # Try to find and load .env file
    env_file = ConfigLoader._find_env_file()
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()  # Fallback to default behavior
    
    # Rest of existing logic...
```

**Test**: Create `.env` in parent directory and verify detection

---

### 1.2 Async URL Detection and Conversion
**File**: `src/migrator/utils/config_loader.py`

**Current Issue**: Async URLs (`postgresql+asyncpg://`) fail with Alembic
**Solution**: Detect and convert async URLs to sync equivalents

```python
@staticmethod
def _normalize_database_url(url: str) -> str:
    """Convert async database URLs to sync for Alembic compatibility"""
    async_drivers = {
        "+asyncpg": "",  # PostgreSQL
        "+aiomysql": "+pymysql",  # MySQL
        "+aiosqlite": "",  # SQLite
    }
    
    original_url = url
    for async_driver, sync_driver in async_drivers.items():
        if async_driver in url:
            url = url.replace(async_driver, sync_driver)
            from migrator.core.logger import warning
            warning(f"Detected async URL: {async_driver}")
            warning(f"Converting to sync for Alembic: {sync_driver or 'default'}")
            break
    
    return url

@staticmethod
def load_database_url() -> str:
    """Auto-detect database URL from multiple sources"""
    # ... existing detection logic ...
    
    if db_url:
        return ConfigLoader._normalize_database_url(db_url)
    
    raise ValueError(...)
```

**Test**: Use `postgresql+asyncpg://` URL and verify conversion

---

### 1.3 Explicit Config File Path
**File**: `src/migrator/core/config.py`

**Current Issue**: No way to specify config file location
**Solution**: Add optional config_path parameter

```python
class MigratorConfig(BaseModel):
    database_url: str
    migrations_dir: Path = Path("migrations")
    base_import_path: Optional[str] = None

    @classmethod
    def load(
        cls, 
        migrations_dir: Optional[Path] = None,
        config_path: Optional[Path] = None
    ) -> "MigratorConfig":
        """Auto-detect config from multiple sources"""
        db_url = ConfigLoader.load_database_url(config_path)
        return cls(
            database_url=db_url, 
            migrations_dir=migrations_dir or Path("migrations")
        )
```

**File**: `src/migrator/utils/config_loader.py`

```python
@staticmethod
def load_database_url(config_path: Optional[Path] = None) -> str:
    """Auto-detect database URL from multiple sources"""
    # If explicit config path provided, try it first
    if config_path:
        db_url = ConfigLoader._try_explicit_config(config_path)
        if db_url:
            return ConfigLoader._normalize_database_url(db_url)
    
    # ... existing detection logic ...

@staticmethod
def _try_explicit_config(config_path: Path) -> Optional[str]:
    """Load from explicitly specified config file"""
    if not config_path.exists():
        return None
    
    if config_path.suffix == ".py":
        # Import Python config
        spec = importlib.util.spec_from_file_location("config", config_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, "DATABASE_URL", None)
    elif config_path.suffix in [".yaml", ".yml"]:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("database", {}).get("url")
    
    return None
```

**Test**: Use `--config backend/settings.py` and verify loading

---

## Phase 2: Base Class Detection Improvements

### 2.1 Expand Common Model Paths
**File**: `src/migrator/core/constants.py`

**Current Issue**: Only checks flat structures
**Solution**: Add nested structure patterns

```python
COMMON_MODEL_PATHS = [
    # Existing
    "app.models",
    "app.database",
    "models",
    "database",
    "src.models",
    "project.models",
    "core.models",
    "db.models",
    
    # New: Nested structures
    "app.core.database",
    "app.core.models",
    "app.db.base",
    "app.db.models",
    "backend.app.models",
    "backend.app.database",
    "backend.core.database",
    "src.app.models",
    "src.app.database",
    "src.core.database",
    "core.database",
    "db.base",
]
```

**Test**: Create Base in `app/core/database.py` and verify detection

---

### 2.2 Explicit Base Path Support
**File**: `src/migrator/core/detector.py`

**Current Issue**: No way to specify Base location
**Solution**: Add method to load Base from explicit path

```python
class ModelDetector:
    """Auto-detect SQLAlchemy Base classes"""

    @classmethod
    def find_base(cls, explicit_path: Optional[str] = None) -> Optional[Any]:
        """Find SQLAlchemy declarative base"""
        # Try explicit path first
        if explicit_path:
            base = cls._try_explicit_path(explicit_path)
            if base:
                return base
        
        # Try common paths
        for path in COMMON_MODEL_PATHS:
            base = cls._try_import(path)
            if base:
                return base

        # Fallback to project scan
        return cls._scan_project()
    
    @staticmethod
    def _try_explicit_path(path: str) -> Optional[Any]:
        """Load Base from explicit path like 'app.core.database:Base'"""
        try:
            if ":" in path:
                module_path, attr_name = path.split(":", 1)
            else:
                module_path = path
                attr_name = "Base"
            
            sys.path.insert(0, str(Path.cwd()))
            module = importlib.import_module(module_path)
            
            if hasattr(module, attr_name):
                obj = getattr(module, attr_name)
                if hasattr(obj, "metadata") and hasattr(obj, "registry"):
                    return obj
        except (ImportError, AttributeError, ValueError) as e:
            from migrator.core.logger import error
            error(f"Failed to load Base from {path}: {e}")
        
        return None
```

**Test**: Use `--base app.core.database:Base` and verify loading

---

### 2.3 Track Searched Paths for Error Reporting
**File**: `src/migrator/core/detector.py`

**Current Issue**: No visibility into what was searched
**Solution**: Track and return searched paths

```python
class ModelDetector:
    """Auto-detect SQLAlchemy Base classes"""
    
    searched_paths: List[str] = []

    @classmethod
    def find_base(cls, explicit_path: Optional[str] = None) -> Optional[Any]:
        """Find SQLAlchemy declarative base"""
        cls.searched_paths = []
        
        # Try explicit path first
        if explicit_path:
            cls.searched_paths.append(explicit_path)
            base = cls._try_explicit_path(explicit_path)
            if base:
                return base
        
        # Try common paths
        for path in COMMON_MODEL_PATHS:
            cls.searched_paths.append(path)
            base = cls._try_import(path)
            if base:
                return base

        # Scan project
        cls.searched_paths.append("project scan")
        return cls._scan_project()
    
    @classmethod
    def get_searched_paths(cls) -> List[str]:
        """Get list of paths that were searched"""
        return cls.searched_paths
```

**Test**: Trigger Base not found and verify paths are tracked

---

## Phase 3: CLI Enhancements

### 3.1 Add --base Flag to init Command
**File**: `src/migrator/cli.py`

**Current Issue**: No way to specify Base location via CLI
**Solution**: Add --base option

```python
@app.command()
def init(
    directory: Path = typer.Option(Path("migrations"), "--dir", "-d", help="Migration directory"),
    base_path: str = typer.Option(None, "--base", "-b", help="Base class path (e.g. app.core.database:Base)"),
    config_path: Path = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Initialize migration environment"""
    try:
        info("Detecting project configuration...")
        config = MigratorConfig.load(migrations_dir=directory, config_path=config_path)

        info("Finding SQLAlchemy Base...")
        base = ModelDetector.find_base(explicit_path=base_path)
        
        if not base:
            error("Could not find SQLAlchemy Base class")
            
            # Show what was searched
            searched = ModelDetector.get_searched_paths()
            if searched:
                info(f"Searched in: {', '.join(searched[:5])}")
                if len(searched) > 5:
                    info(f"... and {len(searched) - 5} more locations")
            
            # Provide helpful hints
            console.print("\n💡 Hints:")
            console.print("  1. Use --base flag: migrator init --base app.core.database:Base")
            console.print("  2. Ensure Base = declarative_base() exists in your code")
            console.print("  3. Check that your models are importable")
            
            raise typer.Exit(1)

        # Rest of existing logic...
```

**Test**: Run without Base and verify helpful error message

---

### 3.2 Add --verbose Flag
**File**: `src/migrator/cli.py`

**Current Issue**: No visibility into detection process
**Solution**: Add verbose mode

```python
@app.command()
def init(
    directory: Path = typer.Option(Path("migrations"), "--dir", "-d", help="Migration directory"),
    base_path: str = typer.Option(None, "--base", "-b", help="Base class path"),
    config_path: Path = typer.Option(None, "--config", "-c", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed detection process"),
):
    """Initialize migration environment"""
    try:
        if verbose:
            info("Verbose mode enabled")
        
        info("Detecting project configuration...")
        
        if verbose:
            env_file = ConfigLoader._find_env_file()
            if env_file:
                info(f"Found .env at: {env_file}")
            else:
                info("No .env file found")
        
        config = MigratorConfig.load(migrations_dir=directory, config_path=config_path)
        
        if verbose:
            info(f"Database URL: {config.database_url[:20]}...")
        
        info("Finding SQLAlchemy Base...")
        base = ModelDetector.find_base(explicit_path=base_path)
        
        if verbose and base:
            info(f"Found Base in: {base.__module__}")
        
        # Rest of logic...
```

**Test**: Run with `--verbose` and verify detailed output

---

### 3.3 Improve makemigrations Command
**File**: `src/migrator/cli.py`

**Current Issue**: Same Base detection issues
**Solution**: Add --base flag to makemigrations

```python
@app.command()
def makemigrations(
    message: str = typer.Argument(..., help="Migration description"),
    autogenerate: bool = typer.Option(True, "--auto/--manual", help="Auto-generate migration"),
    base_path: str = typer.Option(None, "--base", "-b", help="Base class path"),
):
    """Create new migration"""
    try:
        config = MigratorConfig.load()

        if not validate_database_url(config.database_url):
            error("Invalid database URL format")
            raise typer.Exit(1)

        # Ensure Base is importable for autogenerate
        if autogenerate and not config.base_import_path:
            base = ModelDetector.find_base(explicit_path=base_path)
            if not base:
                error("Could not find SQLAlchemy Base class")
                info("Hint: Use --base flag or run 'migrator init' first")
                raise typer.Exit(1)

        # Rest of logic...
```

**Test**: Run makemigrations with --base flag

---

## Phase 4: Documentation Updates

### 4.1 Update README.md
**File**: `README.md`

Add section for nested structures and async projects:

```markdown
## 🏗️ Advanced Usage

### Nested Project Structures

If your Base is in a nested module:

```bash
migrator init --base app.core.database:Base
```

### Async SQLAlchemy Projects

Migrator automatically converts async URLs for Alembic:

```bash
# Your .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Migrator converts to: postgresql://user:pass@localhost/db
```

### Custom Config Location

```bash
migrator init --config backend/settings.py
```

### Verbose Mode

```bash
migrator init --verbose  # See what's being detected
```
```

---

### 4.2 Create ASYNC_GUIDE.md
**File**: `ASYNC_GUIDE.md`

New guide for async SQLAlchemy users:

```markdown
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
```

---

### 4.3 Update MIGRATION_GUIDE.md
**File**: `MIGRATION_GUIDE.md`

Add section for nested structures:

```markdown
## Scenario 5: Nested Project Structure

If your Base is in a nested module like `app/core/database.py`:

```bash
# Initialize with explicit Base path
migrator init --base app.core.database:Base

# Or set in environment
export MIGRATOR_BASE_PATH=app.core.database:Base
migrator init
```
```

---

## Phase 5: Testing

### 5.1 New Test Cases
**File**: `tests/test_nested_structure.py`

```python
def test_nested_base_detection(temp_dir):
    """Test Base detection in nested structure"""
    # Create app/core/database.py
    app_dir = temp_dir / "app" / "core"
    app_dir.mkdir(parents=True)
    
    (app_dir / "__init__.py").write_text("")
    (temp_dir / "app" / "__init__.py").write_text("")
    
    (app_dir / "database.py").write_text("""
from sqlalchemy.orm import declarative_base
Base = declarative_base()
""")
    
    base = ModelDetector.find_base()
    assert base is not None

def test_explicit_base_path(temp_dir):
    """Test explicit Base path"""
    # Create structure
    # ...
    
    base = ModelDetector.find_base(explicit_path="app.core.database:Base")
    assert base is not None

def test_async_url_conversion():
    """Test async URL conversion"""
    url = "postgresql+asyncpg://user:pass@localhost/db"
    converted = ConfigLoader._normalize_database_url(url)
    assert "+asyncpg" not in converted
    assert "postgresql://" in converted
```

**File**: `tests/test_config_discovery.py`

```python
def test_env_file_in_parent_directory(temp_dir):
    """Test .env discovery in parent directory"""
    # Create nested structure
    backend_dir = temp_dir / "backend"
    backend_dir.mkdir()
    
    # Put .env in parent
    (temp_dir / ".env").write_text("DATABASE_URL=postgresql://test")
    
    # Change to backend dir
    os.chdir(backend_dir)
    
    url = ConfigLoader.load_database_url()
    assert url == "postgresql://test"

def test_explicit_config_path(temp_dir):
    """Test explicit config file path"""
    config_file = temp_dir / "backend" / "settings.py"
    config_file.parent.mkdir()
    config_file.write_text('DATABASE_URL = "postgresql://explicit"')
    
    url = ConfigLoader.load_database_url(config_path=config_file)
    assert url == "postgresql://explicit"
```

---

## Phase 6: Version Update

### 6.1 Update Version
**Files**: `pyproject.toml`, `src/migrator/__init__.py`

Change version to `0.2.1`

---

### 6.2 Update CHANGELOG.md

```markdown
## [0.2.1] - 2025-01-XX

### Added
- `--base` flag to specify Base class location explicitly
- `--config` flag to specify config file path
- `--verbose` flag for detailed detection output
- Automatic async URL conversion (asyncpg, aiomysql, aiosqlite)
- Multi-directory .env file search (searches up 5 parent directories)
- Support for nested project structures (app.core.database)
- Expanded common model paths for better auto-detection
- Detailed error messages showing searched paths

### Fixed
- .env file not found in parent directories
- Base class detection in nested structures
- Async SQLAlchemy URL compatibility
- Poor error messages with no actionable information

### Documentation
- Added ASYNC_GUIDE.md for async SQLAlchemy projects
- Updated README with advanced usage examples
- Added nested structure examples to MIGRATION_GUIDE.md
```

---

## Implementation Order

1. **Day 1**: Phase 1 (Config Discovery) - 2 hours
2. **Day 2**: Phase 2 (Base Detection) - 3 hours
3. **Day 3**: Phase 3 (CLI Enhancements) - 2 hours
4. **Day 4**: Phase 4 (Documentation) - 1 hour
5. **Day 5**: Phase 5 (Testing) - 2 hours
6. **Day 6**: Phase 6 (Release) - 1 hour

**Total**: ~11 hours over 6 days

---

## Success Criteria

- ✅ .env file found in parent directories
- ✅ Base detected in `app/core/database.py`
- ✅ Async URLs automatically converted
- ✅ `--base` flag works
- ✅ `--config` flag works
- ✅ `--verbose` shows detection process
- ✅ Error messages show searched paths
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Invoice Generator API feedback addressed

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing users | Low | High | Maintain backward compatibility |
| Import errors with explicit paths | Medium | Medium | Comprehensive error handling |
| Performance impact from parent dir search | Low | Low | Limit to 5 levels |
| Async URL conversion edge cases | Medium | Medium | Extensive testing |

---

## Post-Release

1. Request feedback from Invoice Generator API team
2. Monitor GitHub issues for new edge cases
3. Consider adding `MIGRATOR_BASE_PATH` environment variable
4. Consider caching detected Base location
