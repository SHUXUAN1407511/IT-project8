from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import os

BASE_DIR = Path(__file__).resolve().parents[1]


def _load_env_file(path: Path) -> None:
    """Populate os.environ with key/value pairs from the provided file."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


for candidate in (BASE_DIR / ".env", BASE_DIR / ".env.development"):
    _load_env_file(candidate)


def _as_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _split_items(raw: str | None, fallback: Iterable[str]) -> list[str]:
    if not raw:
        return [item for item in fallback]
    return [item.strip() for item in raw.split(",") if item.strip()]


def _build_database_config() -> dict[str, str]:
    engine = (os.getenv("DJANGO_DB_ENGINE") or "sqlite").strip().lower()
    if engine in {"mysql", "mariadb"}:
        return {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DJANGO_DB_NAME", ""),
            "USER": os.getenv("DJANGO_DB_USER", ""),
            "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
            "HOST": os.getenv("DJANGO_DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DJANGO_DB_PORT", "3306"),
        }
    if engine in {"postgres", "postgresql"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DJANGO_DB_NAME", ""),
            "USER": os.getenv("DJANGO_DB_USER", ""),
            "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
            "HOST": os.getenv("DJANGO_DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
        }
    sqlite_name = os.getenv("DJANGO_SQLITE_NAME", "db.sqlite3")
    sqlite_path = Path(os.getenv("DJANGO_SQLITE_PATH", "") or BASE_DIR / sqlite_name)
    if not sqlite_path.is_absolute():
        sqlite_path = (BASE_DIR / sqlite_path).resolve()
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(sqlite_path),
    }


@dataclass(slots=True)
class AppEnvironment:
    secret_key: str
    debug: bool
    allowed_hosts: list[str]
    cors_allowed_origins: list[str]
    csrf_trusted_origins: list[str]
    database: dict[str, str]
    email_backend: str
    email_host: str
    email_port: int
    email_host_user: str
    email_host_password: str
    email_use_tls: bool
    email_use_ssl: bool
    default_from_email: str
    password_reset_url: str
    password_reset_token_expiry_minutes: int


def load_environment() -> AppEnvironment:
    secret = os.getenv("DJANGO_SECRET_KEY") or "dev-secret-change-me"
    debug_default = secret.startswith("dev-")
    debug_flag = _as_bool(os.getenv("DJANGO_DEBUG"), debug_default)

    allowed_hosts = _split_items(
        os.getenv("DJANGO_ALLOWED_HOSTS"),
        ("127.0.0.1", "localhost"),
    )
    default_cors_origins = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    )
    cors_origins = _split_items(
        os.getenv("DJANGO_CORS_ORIGINS"),
        default_cors_origins,
    )
    csrf_trusted = _split_items(
        os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS"),
        cors_origins,
    )

    email_backend = os.getenv(
        "EMAIL_BACKEND",
        "django.core.mail.backends.console.EmailBackend",
    )
    email_host = os.getenv("EMAIL_HOST", "")
    email_port = int(os.getenv("EMAIL_PORT", "587"))
    email_use_tls = _as_bool(os.getenv("EMAIL_USE_TLS"), True)
    email_use_ssl = _as_bool(os.getenv("EMAIL_USE_SSL"), False)
    if email_use_ssl:
        email_use_tls = False

    return AppEnvironment(
        secret_key=secret,
        debug=debug_flag,
        allowed_hosts=allowed_hosts,
        cors_allowed_origins=cors_origins,
        csrf_trusted_origins=csrf_trusted,
        database=_build_database_config(),
        email_backend=email_backend,
        email_host=email_host,
        email_port=email_port,
        email_host_user=os.getenv("EMAIL_HOST_USER", ""),
        email_host_password=os.getenv("EMAIL_HOST_PASSWORD", ""),
        email_use_tls=email_use_tls,
        email_use_ssl=email_use_ssl,
        default_from_email=os.getenv("DEFAULT_FROM_EMAIL", "AI Use Declaration <no-reply@example.com>"),
        password_reset_url=os.getenv(
            "PASSWORD_RESET_URL",
            "http://localhost:5173/reset-password",
        ),
        password_reset_token_expiry_minutes=int(
            os.getenv("PASSWORD_RESET_TOKEN_EXPIRY_MINUTES", "30")
        ),
    )


env = load_environment()
