from pathlib import Path
from typing import Any

from .settings import ApplicationSettings

# This will be root of the project
BASEDIR = Path(__file__).resolve().parents[2]


class BaseConfig:
    ENV = "base"

    SECRET_KEY = ApplicationSettings.defaults["secret_key"]

    # Disable tracking to save on memory and performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_app(cls, app):
        """
        Finalize config after environment overrides are applied.
        This is the ONLY place derived values should be computed.
        """
        app.config["SQLALCHEMY_DATABASE_URI"] = cls.build_database_uri(app.config)

    @classmethod
    def build_database_uri(cls, config: dict[str, Any]) -> str:
        db_type = config.get("DB_TYPE")

        if db_type in ("postgres", "postgresql"):
            return (
                f"postgresql://{config['DB_USER']}:{config['DB_PASSWORD']}"
                f"@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"
            )

        if db_type == "sqlite":
            db_path = config.get("DB_PATH") or ":memory:"
            return f"sqlite:///{db_path}"

        raise ValueError(f"Unsupported DB_TYPE: {config.get('DB_TYPE')}")
