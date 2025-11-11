from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import os


class MigratorConfig(BaseModel):
    database_url: str
    migrations_dir: Path = Path("migrations")
    base_import_path: Optional[str] = None
    
    @classmethod
    def load(cls) -> "MigratorConfig":
        """Auto-detect config from multiple sources"""
        load_dotenv()
        
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            db_url = cls._try_settings_py()
        
        if not db_url:
            db_url = cls._try_config_yaml()
        
        if not db_url:
            raise ValueError("DATABASE_URL not found in .env, settings.py, or config.yaml")
        
        return cls(database_url=db_url)
    
    @staticmethod
    def _try_settings_py() -> Optional[str]:
        try:
            from settings import DATABASE_URL
            return DATABASE_URL
        except:
            return None
    
    @staticmethod
    def _try_config_yaml() -> Optional[str]:
        try:
            import yaml
            with open("config.yaml") as f:
                config = yaml.safe_load(f)
                return config.get("database", {}).get("url")
        except:
            return None
