"""FastAPI app exposing POST /ask."""

from fastapi import FastAPI

from support_assistant.graph import build_graph
from support_assistant.schemas import AskRequest, AskResponse

app = FastAPI(title="Zepto Support Assistant")

graph_app = build_graph()


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    result = graph_app.invoke({"query": request.query})
    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
    )
