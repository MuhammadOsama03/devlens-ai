import pytest

from app.qa import (
    MAX_CONTEXT_LENGTH,
    ContextFile,
    build_context_chunks,
    build_grounded_prompt,
    prepare_repository_question,
)


def test_prepares_bounded_repository_context():
    request = prepare_repository_question(
        "example/project",
        "  Where   is auth configured? ",
        ["config.py: AUTH_ENABLED=True", "routes.py: /login"],
    )

    assert request.question == "Where is auth configured?"
    assert "config.py" in request.context
    assert len(request.context) <= MAX_CONTEXT_LENGTH + 40


def test_prompt_marks_repository_content_as_untrusted():
    request = prepare_repository_question("example/project", "What does it do?", ["README"])
    prompt = build_grounded_prompt(request)

    assert "untrusted data" in prompt
    assert "Answer only from" in prompt


@pytest.mark.parametrize("question", ["", "   "])
def test_rejects_empty_questions(question):
    with pytest.raises(ValueError, match="cannot be empty"):
        prepare_repository_question("example/project", question, [])


def test_context_chunks_label_files_and_redact_secrets():
    chunks = build_context_chunks(
        [ContextFile(path="config.py", content="API_KEY=super-secret\nDEBUG=false")]
    )

    assert chunks == ["FILE: config.py\nAPI_KEY=[REDACTED]\nDEBUG=false"]


def test_context_chunks_skip_empty_files():
    assert build_context_chunks([ContextFile(path="empty.txt", content="  ")]) == []
