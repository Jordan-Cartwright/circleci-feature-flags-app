import os
from typing import Any


class ApplicationSettings(object):
    defaults = {
        "secret_key": "super-secret-key",
        "bind_address": "127.0.0.1",
        # Database Settings
        "db_type": "postgres",
        "db_host": "127.0.0.1",
        "db_port": 5432,
        "db_user": "postgres",
        "db_password": "password",
        "db_name": "feature_flags",
    }

    types = {
        "secret_key": str,
        "bind_address": str,
        # Database Settings
        "db_type": str,
        "db_host": str,
        "db_port": int,
        "db_user": str,
        "db_password": str,
        "db_name": str,
    }

    @staticmethod
    def convert_type(name: str, value: Any):
        if name in ApplicationSettings.types:
            var_type = ApplicationSettings.types[name]

            # Handle boolean values
            if var_type == bool and isinstance(value, str):
                if value.lower() in ["true", "yes", "t", "1"] or value is True:
                    return True
                return False

            # Handle integer values
            if var_type == int:
                return int(value)

            # Handle string values
            if var_type == str:
                return str(value)

        return value

    @staticmethod
    def load_environment(app):
        """Load app settings from environment variables when defined"""

        for var_name, default_value in ApplicationSettings.defaults.items():
            env_name = var_name.upper()
            current_value = None

            if env_name + "_FILE" in os.environ:
                if env_name in os.environ:
                    raise AttributeError(
                        "Both {} and {} are set but are exclusive.".format(env_name, env_name + "_FILE")
                    )
                with open(os.environ[env_name + "_FILE"]) as f:
                    current_value = f.read().strip()

            elif env_name in os.environ:
                current_value = os.environ[env_name]

            if current_value is not None:
                app.config[env_name] = ApplicationSettings.convert_type(var_name, current_value)
