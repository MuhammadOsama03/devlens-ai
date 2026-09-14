import pytest

from app.qa import MAX_CONTEXT_LENGTH, build_grounded_prompt, prepare_repository_question


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
