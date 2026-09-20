from app.conversations.service import ConversationService


def test_conversation_service_creates_and_lists_conversations(tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")

    conversation = service.create_conversation(title="Test chat")

    assert conversation.title == "Test chat"
    assert service.get_conversation(conversation.id).title == "Test chat"
    assert service.list_conversations()[0].id == conversation.id


def test_conversation_service_adds_and_lists_messages(tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    conversation = service.create_conversation()

    service.add_message(conversation.id, "user", "hello")
    service.add_message(conversation.id, "assistant", "hi there")

    messages = service.list_messages(conversation.id)

    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["hello", "hi there"]


def test_conversation_service_builds_bounded_context(tmp_path):
    service = ConversationService(database_path=tmp_path / "conversations.db")
    conversation = service.create_conversation()

    for role, content in [
        ("user", "first question"),
        ("assistant", "first answer"),
        ("user", "second question"),
        ("assistant", "second answer"),
        ("user", "third question"),
    ]:
        service.add_message(conversation.id, role, content)

    recent_messages = service.get_recent_messages(conversation.id, max_turns=2)
    context = service.get_recent_context(conversation.id, max_turns=2)

    assert [message.content for message in recent_messages] == ["second answer", "third question"]
    assert "User: third question" in context
    assert "first question" not in context
