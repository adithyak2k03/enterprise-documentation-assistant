from app.llm.service import create_llm


def test_create_llm():
    llm = create_llm()

    assert llm is not None
    assert llm.model == "gemini-2.5-flash"
