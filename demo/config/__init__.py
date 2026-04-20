from .development import DevelopmentConfig
from .local import LocalConfig
from .production import ProductionConfig
from .testing import TestingConfig

# Map environment names to their configuration classes
Config = {
    "local": LocalConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": LocalConfig,
}
