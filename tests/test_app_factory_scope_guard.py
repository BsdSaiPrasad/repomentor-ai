from backend.app_factory.scope_guard import evaluate_scope


def test_scope_guard_allows_small_single_user_app():
    result = evaluate_scope("Build a flashcard app for studying prompt engineering")

    assert result.allowed is True
    assert result.complexity_score <= 2
    assert result.risk_level == "low"


def test_scope_guard_reduces_payment_auth_request():
    result = evaluate_scope("Build a marketplace with login and Stripe payments")

    assert result.allowed is False
    assert result.reduced_scope is not None
    assert result.requires_human_approval is True

