import os
from pathlib import Path
from typing import List, Optional

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from mako.template import Template

from migrator.core.base import MigrationBackend
from migrator.core.config import MigratorConfig


class AlembicBackend(MigrationBackend):
    """Alembic implementation of migration backend"""
    
    def __init__(self, config: MigratorConfig):
        self.config = config
        self.alembic_cfg = self._create_alembic_config()
    
    def _create_alembic_config(self) -> Config:
        """Create Alembic configuration"""
        cfg = Config()
        cfg.set_main_option("script_location", str(self.config.migrations_dir))
        cfg.set_main_option("sqlalchemy.url", self.config.database_url)
        return cfg
    
    def init(self, directory: Path) -> None:
        """Initialize migration environment"""
        directory.mkdir(parents=True, exist_ok=True)
        versions_dir = directory / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        self._create_env_py(directory)
        self._create_script_mako(directory)
        self._create_alembic_ini(directory)
    
    def _create_env_py(self, directory: Path) -> None:
        """Create customized env.py"""
        template_path = Path(__file__).parent.parent / "templates" / "env.py.mako"
        with open(template_path) as f:
            template = Template(f.read())
        
        if self.config.base_import_path:
            parts = self.config.base_import_path.rsplit(".", 1)
            module_path = parts[0]
            base_name = parts[1]
            imports = f"from {module_path} import {base_name}"
            target_metadata = f"{base_name}.metadata"
        else:
            imports = "# Import your Base here"
            target_metadata = "None"
        
        content = template.render(
            imports=imports,
            target_metadata=target_metadata
        )
        
        env_path = directory / "env.py"
        with open(env_path, "w") as f:
            f.write(content)
    
    def _create_script_mako(self, directory: Path) -> None:
        """Copy script.py.mako template"""
        template_path = Path(__file__).parent.parent / "templates" / "script.py.mako"
        dest_path = directory / "script.py.mako"
        
        with open(template_path) as f:
            content = f.read()
        
        with open(dest_path, "w") as f:
            f.write(content)
    
    def _create_alembic_ini(self, directory: Path) -> None:
        """Create alembic.ini file"""
        ini_content = f"""[alembic]
script_location = {directory}
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        ini_path = directory / "alembic.ini"
        with open(ini_path, "w") as f:
            f.write(ini_content)
    
    def create_migration(self, message: str, autogenerate: bool = True) -> Path:
        """Create new migration"""
        command.revision(
            self.alembic_cfg,
            message=message,
            autogenerate=autogenerate
        )
        return self._get_latest_migration()
    
    def _get_latest_migration(self) -> Path:
        """Get path to latest migration file"""
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        revisions = list(script_dir.walk_revisions())
        if revisions:
            latest = revisions[0]
            return Path(latest.path)
        return Path()
    
    def apply_migrations(self, revision: str = "head") -> None:
        """Apply migrations"""
        command.upgrade(self.alembic_cfg, revision)
    
    def downgrade(self, revision: str = "-1") -> None:
        """Rollback migrations"""
        command.downgrade(self.alembic_cfg, revision)
    
    def history(self) -> List[dict]:
        """Get migration history"""
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        revisions = []
        
        for revision in script_dir.walk_revisions():
            revisions.append({
                "revision": revision.revision,
                "message": revision.doc or "No message",
                "down_revision": revision.down_revision
            })
        
        return list(reversed(revisions))
    
    def current(self) -> Optional[str]:
        """Get current revision"""
        engine = create_engine(self.config.database_url)
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
        
        return current_rev
