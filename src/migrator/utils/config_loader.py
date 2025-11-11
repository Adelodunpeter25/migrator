import os
import sys
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """Load database URL from multiple sources"""

    @staticmethod
    def load_database_url() -> str:
        """Auto-detect database URL from multiple sources"""
        load_dotenv()

        sources = [
            ("DATABASE_URL environment variable", ConfigLoader._try_env),
            ("SQLALCHEMY_DATABASE_URI environment variable", ConfigLoader._try_sqlalchemy_env),
            ("settings.py", ConfigLoader._try_settings_py),
            ("config.py", ConfigLoader._try_config_py),
            ("config.yaml", ConfigLoader._try_config_yaml),
            ("config.toml", ConfigLoader._try_config_toml),
        ]

        for source_name, source_func in sources:
            db_url = source_func()
            if db_url:
                return db_url

        raise ValueError(
            "DATABASE_URL not found. Please set it in:\n"
            "  - .env file (DATABASE_URL=...)\n"
            "  - Environment variable\n"
            "  - settings.py or config.py\n"
            "  - config.yaml or config.toml"
        )

    @staticmethod
    def _try_env() -> Optional[str]:
        return os.getenv("DATABASE_URL")

    @staticmethod
    def _try_sqlalchemy_env() -> Optional[str]:
        return os.getenv("SQLALCHEMY_DATABASE_URI")

    @staticmethod
    def _try_settings_py() -> Optional[str]:
        try:
            sys.path.insert(0, str(Path.cwd()))
            from settings import DATABASE_URL

            return DATABASE_URL
        except (ImportError, AttributeError):
            try:
                from settings import SQLALCHEMY_DATABASE_URI

                return SQLALCHEMY_DATABASE_URI
            except (ImportError, AttributeError):
                return None

    @staticmethod
    def _try_config_py() -> Optional[str]:
        try:
            sys.path.insert(0, str(Path.cwd()))
            from config import DATABASE_URL

            return DATABASE_URL
        except (ImportError, AttributeError):
            try:
                from config import SQLALCHEMY_DATABASE_URI

                return SQLALCHEMY_DATABASE_URI
            except (ImportError, AttributeError):
                return None

    @staticmethod
    def _try_config_yaml() -> Optional[str]:
        try:
            with open("config.yaml") as f:
                config = yaml.safe_load(f)
                return config.get("database", {}).get("url") or config.get("database_url")
        except (FileNotFoundError, yaml.YAMLError, AttributeError):
            return None

    @staticmethod
    def _try_config_toml() -> Optional[str]:
        try:
            import tomllib

            with open("config.toml", "rb") as f:
                config = tomllib.load(f)
                return config.get("database", {}).get("url") or config.get("database_url")
        except (ImportError, FileNotFoundError, Exception):
            return None
