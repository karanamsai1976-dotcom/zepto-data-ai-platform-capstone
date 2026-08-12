"""Offline tests for graph.py -- both routing branches, retrieval correctness,
canned strings, and confidence bounds. Runs entirely with MOCK_LLM unset
(the graded default)."""

from support_assistant.graph import build_graph


def test_policy_question_routes_to_retrieve_and_answer():
    app = build_graph()
    result = app.invoke({"query": "What is the delivery fee?"})

    assert result["intent"] == "policy_question"
    assert result["answer"].startswith("Based on the retrieved context: ")
    assert len(result["sources"]) > 0


def test_general_question_routes_to_direct_answer():
    app = build_graph()
    result = app.invoke({"query": "Who won the world cup?"})

    assert result["intent"] == "general_question"
    assert result["answer"] == "I can only answer questions about Zepto policies right now."
    assert result["sources"] == []


def test_retrieval_hits_the_right_document():
    """A delivery-fee question should retrieve doc_01 (Delivery Policy) as its
    top match."""
    app = build_graph()
    result = app.invoke({"query": "What is the delivery fee?"})

    assert result["sources"][0] == "doc_01#0"


def test_cancellation_question_routes_to_policy_and_hits_doc_05():
    app = build_graph()
    result = app.invoke({"query": "Can I cancel my order?"})

    assert result["intent"] == "policy_question"
    assert result["sources"][0] == "doc_05#0"


def test_confidence_is_within_bounds():
    app = build_graph()
    result = app.invoke({"query": "What is the delivery fee?"})

    assert 0.0 <= result["confidence"] <= 1.0


def test_keyword_substring_match_cancellation():
    """'cancellation' should match the 'cancel' keyword via substring matching."""
    app = build_graph()
    result = app.invoke({"query": "What is your cancellation policy?"})

    assert result["intent"] == "policy_question"
