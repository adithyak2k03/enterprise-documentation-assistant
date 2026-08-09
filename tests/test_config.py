from app.config import settings


def test_settings_load():
    assert settings.llm_provider
    assert settings.llm_model
    assert settings.llm_api_key
    assert settings.langsmith_tracing
    assert settings.langsmith_api_key
    assert settings.langsmith_project
