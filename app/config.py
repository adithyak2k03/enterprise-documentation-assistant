from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str
    llm_model: str
    llm_api_key: str

    langsmith_tracing: bool = True
    langsmith_api_key: str
    langsmith_project: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
