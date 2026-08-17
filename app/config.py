from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    app_base_url: str = "http://localhost:8000"

    database_url: str = "postgresql+psycopg://swb_app:changeme@localhost:5432/studentwellbeing"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    agent_model: str = "deepseek-v4-pro"
    agent_max_tokens: int = 8192

    jwt_secret_key: str = "insecure-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    moderate_risk_threshold: int = 40
    high_risk_threshold: int = 70

    default_language_code: str = "ms"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from_name: str = "Student Well-Being — KPM"


settings = Settings()
