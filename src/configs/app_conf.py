from pydantic_settings import SettingsConfigDict

from .deployment_conf import DeploymentConfig
from .feature_conf import FeatureConfig
from .log_conf import LoggingConfig


class InvoiceInferConfig(DeploymentConfig, LoggingConfig, FeatureConfig):
    model_config = SettingsConfigDict(env_file=".config", env_file_encoding="utf-8", extra="ignore")
