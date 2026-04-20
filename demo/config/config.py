from pathlib import Path

from .settings import ApplicationSettings

# This will be root of the project
BASEDIR = Path(__file__).resolve().parents[2]


class BaseConfig:
    ENV = "base"

    SECRET_KEY = ApplicationSettings.defaults["secret_key"]

    # Disable tracking to save on memory and performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        """
        Finalize config after environment overrides are applied.
        This is the ONLY place derived values should be computed.
        """

        config = app.config

        if config.get("DB_TYPE") == "postgresql" or config.get("DB_TYPE") == "postgres":
            config["SQLALCHEMY_DATABASE_URI"] = (
                f"postgresql://{config['DB_USER']}:{config['DB_PASSWORD']}"
                f"@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"
            )
        else:
            raise ValueError(f"Unsupported DB_TYPE: {config.get('DB_TYPE')}")
