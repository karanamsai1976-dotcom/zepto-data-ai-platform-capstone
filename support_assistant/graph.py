"""LangGraph StateGraph with three nodes: classify_intent, retrieve_and_answer,
direct_answer. Routing does NOT depend on MOCK_LLM -- only generation inside
retrieve_and_answer does."""

from typing import TypedDict

from langgraph.graph import StateGraph, END

from support_assistant.config import MOCK_LLM, POLICY_KEYWORDS
from support_assistant.ingest import retrieve


class GraphState(TypedDict):
    query: str
    intent: str
    answer: str
    sources: list[str]
    confidence: float


def classify_intent(state: GraphState) -> GraphState:
    """Keyword heuristic, no LLM call, regardless of MOCK_LLM."""
    query_lower = state["query"].lower()
    if any(keyword in query_lower for keyword in POLICY_KEYWORDS):
        intent = "policy_question"
    else:
        intent = "general_question"
    return {**state, "intent": intent}


def route_after_classify(state: GraphState) -> str:
    return "retrieve_and_answer" if state["intent"] == "policy_question" else "direct_answer"


def retrieve_and_answer(state: GraphState) -> GraphState:
    results = retrieve(state["query"])
    top_ids = results["ids"][0]
    top_texts = results["documents"][0]

    top_chunk_snippet = top_texts[0][:200] if top_texts else ""

    if MOCK_LLM:
        answer = f"Based on the retrieved context: {top_chunk_snippet}"
    else:
        # Real-LLM generation lives in llm.py, imported only here so the
        # module is never imported at module scope.
        from support_assistant.llm import generate_answer
        answer = generate_answer(state["query"], top_texts)

    return {
        **state,
        "answer": answer,
        "sources": list(top_ids),
        "confidence": 1.0,
    }


def direct_answer(state: GraphState) -> GraphState:
    if MOCK_LLM:
        answer = "I can only answer questions about Zepto policies right now."
    else:
        from support_assistant.llm import generate_direct_answer
        answer = generate_direct_answer(state["query"])

    return {
        **state,
        "answer": answer,
        "sources": [],
        "confidence": 1.0,
    }


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_and_answer", retrieve_and_answer)
    graph.add_node("direct_answer", direct_answer)

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges("classify_intent", route_after_classify, {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    })
    graph.add_edge("retrieve_and_answer", END)
    graph.add_edge("direct_answer", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    print("=== Policy question ===")
    result = app.invoke({"query": "What is the delivery fee?"})
    print(result)

    print("\n=== General question ===")
    result = app.invoke({"query": "Who won the world cup?"})
    print(result)
