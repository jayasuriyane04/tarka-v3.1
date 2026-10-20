"""V3 settings: isolated database/cookies/configuration; no v1 secrets are copied."""
from pathlib import Path
import math
from typing import Literal
from urllib.parse import urlparse
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    app_env: Literal['development', 'test', 'production'] = 'development'
    database_url: str = 'sqlite:///' + (ROOT / 'backend/tarka-v3-dev.db').as_posix()
    session_secret: str = 'development-v3-change-before-deployment'
    cookie_secure: bool = False
    allowed_origins: str = 'http://localhost:5175,http://127.0.0.1:5175,http://localhost:8003,http://127.0.0.1:8003'
    nebius_api_key: str = ''
    nebius_base_url: str = 'https://api.tokenfactory.nebius.com/v1/'
    nebius_model: str = 'nvidia/Nemotron-3_5-Lightning'
    enable_paid_operations: bool = False
    paid_budget_usd: float = 0
    nebius_input_usd_per_million: float = 0.06
    nebius_output_usd_per_million: float = 0.24
    model_max_tokens: int = 512
    parent_token_seconds: int = 600
    break_seconds: int = 60
    auth_session_seconds: int = 7 * 86400
    auth_idle_seconds: int = 86400

    def validate_deployment(self):
        if not 3600 <= self.auth_session_seconds <= 7 * 86400 or not 900 <= self.auth_idle_seconds <= 86400:
            raise ValueError('Account sessions must have bounded absolute and idle lifetimes.')
        if not math.isfinite(self.paid_budget_usd) or self.paid_budget_usd < 0:
            raise ValueError('Budget must be finite and nonnegative.')
        if self.enable_paid_operations and self.paid_budget_usd <= 0:
            raise ValueError('Paid calls require a positive authorized ceiling.')
        if any(not math.isfinite(x) or x <= 0 for x in (self.nebius_input_usd_per_million, self.nebius_output_usd_per_million)):
            raise ValueError('Configure positive finite model rates.')
        if not 256 <= self.model_max_tokens <= 4096 or not 60 <= self.parent_token_seconds <= 900 or not 30 <= self.break_seconds <= 300:
            raise ValueError('Invalid output/session limits.')
        if self.app_env == 'production':
            if len(self.session_secret) < 32 or self.session_secret.startswith('development') or not self.cookie_secure:
                raise ValueError('Production requires a random session secret and secure cookies.')
            if not self.database_url.startswith('postgresql'):
                raise ValueError('Production requires PostgreSQL.')
            origins = self.allowed_origins.split(',')
            for origin in origins:
                parsed = urlparse(origin.strip())
                if parsed.scheme != 'https' or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username or '*' in origin:
                    raise ValueError('Production requires exact HTTPS origins.')


settings = Settings()
