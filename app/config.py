from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./leadgen.db"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "LeadGen <no-reply@example.com>"

    imap_host: str = "imap.gmail.com"
    imap_username: str = ""
    imap_password: str = ""
    imap_folder: str = "INBOX"

    app_base_url: str = "http://localhost:8000"
    secret_key: str = "change_me_secret"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    daily_send_limit: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
