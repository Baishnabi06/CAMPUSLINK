from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str
    database_name: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    cors_origins: str = "http://127.0.0.1:5500"

    # Email (SMTP) settings used to send OTP login codes.
    # Defaults let the app start even if SMTP isn't configured yet.
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    otp_expire_minutes: int = 5

    # Optional: AI-written readiness analysis (leave the key empty to switch it off)
    anthropic_api_key: str = ""
    ai_model: str = "claude-haiku-4-5-20251001"

    # Google Calendar / Meet (used to create interview meeting links).
    # Values come from Backend/.env as GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    # and GOOGLE_REFRESH_TOKEN. Never put the real values in this file.
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()