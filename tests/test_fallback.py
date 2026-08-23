import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from unittest.mock import patch, MagicMock
from src.assistant import run_assistant

def mock_resolve_policy(question, determination_date=None, change_date=None):
    q = question.lower()
    if "income threshold" in q:
        if determination_date is None and change_date is None:
            return {"status": "NEEDS_DATE", "needs_date": "determination_date", "top_score": 0.85}
        text = "1: $1,225; 2: $1,650; 3: $2,075;" if determination_date == "2026-04-25" else "1: $1,180; 2: $1,590; 3: $2,000;"
        return {
            "status": "RESOLVED",
            "applicable": [{"clause_id": "6.6.1", "source_doc": "Policy", "text": text}],
            "top_score": 0.85
        }
    elif "report a change" in q:
        if determination_date is None and change_date is None:
            return {"status": "NEEDS_DATE", "needs_date": "change_of_circumstance_date", "top_score": 0.85}
        text = "within 14 calendar days" if change_date == "2026-04-25" else "within 10 calendar days"
        return {
            "status": "RESOLVED",
            "applicable": [{"clause_id": "4.3.2", "source_doc": "Policy", "text": text}],
            "top_score": 0.85
        }
    elif "capital" in q or "medication" in q:
        return {"status": "ABSTAIN", "top_score": 0.1}
    return {"status": "NOT_FOUND"}

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_gemini_success(mock_generate, mock_resolve):
    mock_generate.return_value = "This is a successful Gemini answer."

    response = run_assistant(
        question="What is the income threshold for a household of 3?",
        determination_date="2026-04-25"
    )
    assert response["status"] == "ANSWERED"
    assert response["generation_mode"] == "gemini"
    assert response["answer"] == "This is a successful Gemini answer."

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_gemini_429_fallback(mock_generate, mock_resolve):
    mock_generate.side_effect = Exception("429 Too Many Requests")

    response = run_assistant(
        question="What is the income threshold for a household of 3?",
        determination_date="2026-04-25"
    )
    assert response["status"] == "ANSWERED"
    assert response["generation_mode"] == "fallback"
    assert "2,075" in response["answer"]

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_gemini_quota_exception_fallback(mock_generate, mock_resolve):
    mock_generate.side_effect = Exception("RESOURCE_EXHAUSTED quota exceeded")

    response = run_assistant(
        question="What is the income threshold for a household of 3?",
        determination_date="2026-04-25"
    )
    assert response["status"] == "ANSWERED"
    assert response["generation_mode"] == "fallback"
    assert "2,075" in response["answer"]

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_needs_date_no_gemini_call(mock_generate, mock_resolve):
    response = run_assistant(
        question="What is the income threshold for a household of 3?"
    )
    assert response["status"] == "NEEDS_DATE"
    mock_generate.assert_not_called()

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_abstain_no_gemini_call(mock_generate, mock_resolve):
    response = run_assistant(
        question="What is the capital of France?"
    )
    assert response["status"] == "ABSTAIN"
    mock_generate.assert_not_called()

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_current_income_policy_fallback(mock_generate, mock_resolve):
    mock_generate.side_effect = Exception("429 Too Many Requests")
    response = run_assistant(
        question="What is the income threshold for a household of 3?",
        determination_date="2026-04-25"
    )
    assert response["status"] == "ANSWERED"
    assert response["answer"] == "The monthly income threshold for a household of 3 is $2,075."

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_historical_income_policy_fallback(mock_generate, mock_resolve):
    mock_generate.side_effect = Exception("429 Too Many Requests")
    response = run_assistant(
        question="What is the income threshold for a household of 3?",
        determination_date="2026-02-15"
    )
    assert response["status"] == "ANSWERED"
    assert response["answer"] == "The monthly income threshold for a household of 3 is $2,000."

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_current_reporting_policy_fallback(mock_generate, mock_resolve):
    mock_generate.side_effect = Exception("429")
    response = run_assistant(
        question="How long does a recipient have to report a change of circumstances?",
        change_date="2026-04-25"
    )
    assert response["status"] == "ANSWERED"
    assert response["answer"] == "A recipient must report a change of circumstances within 14 calendar days."

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_historical_reporting_policy_fallback(mock_generate, mock_resolve):
    mock_generate.side_effect = Exception("429")
    response = run_assistant(
        question="How long does a recipient have to report a change of circumstances?",
        change_date="2026-02-15"
    )
    assert response["status"] == "ANSWERED"
    assert response["answer"] == "A recipient must report a change of circumstances within 10 calendar days."

@patch("src.assistant.resolve_policy", side_effect=mock_resolve_policy)
@patch("src.assistant.generate_answer")
def test_unsupported_question_abstain(mock_generate, mock_resolve):
    response = run_assistant(
        question="What is the capital of France?",
        determination_date="2026-04-25"
    )
    assert response["status"] == "ABSTAIN"
    mock_generate.assert_not_called()
