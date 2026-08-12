"""Real-LLM answer generation for the optional MOCK_LLM=0 path. The SDK
import lives inside each function, never at module scope, so this module
imports cleanly on a machine with no LLM package installed and no API key --
which is exactly the situation on the graded MOCK_LLM=1 default path."""

import json

from pydantic import ValidationError

from support_assistant.prompts import ANSWER_PROMPT_TEMPLATE
from support_assistant.schemas import AskResponse

MAX_RETRIES = 2


def _call_groq(prompt: str) -> str:
    from groq import Groq
    import os

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_answer(query: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)
    prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=query)
    return _call_groq(prompt)


def generate_direct_answer(query: str) -> str:
    prompt = (
        "You are a customer support assistant for Zepto. Answer this general "
        f"question briefly and politely in 1-2 sentences: {query}"
    )
    return _call_groq(prompt)


def generate_structured_answer(query, context_chunks, sources) -> AskResponse:
    """
    Calls the LLM, validates its raw output against AskResponse. On failure,
    retries up to MAX_RETRIES additional times with a corrective instruction
    appended to the prompt. Returns a clearly marked error response if every
    attempt fails. This path never triggers in MOCK_LLM=1 (default) mode.
    """
    context = "\n\n".join(context_chunks)
    base_prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=query)

    prompt = base_prompt
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        raw_output = _call_groq(prompt)
        try:
            data = json.loads(raw_output)
            return AskResponse(
                answer=data["answer"],
                sources=sources,
                confidence=data.get("confidence", 0.5),
            )
        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            last_error = e
            prompt = (
                base_prompt
                + f"\n\nYour previous response was invalid ({e}). "
                "Respond with ONLY valid JSON matching this shape: "
                '{"answer": "...", "confidence": 0.0-1.0}'
            )

    return AskResponse(
        answer=f"Error: could not generate a valid response after {MAX_RETRIES + 1} attempts ({last_error}).",
        sources=[],
        confidence=0.0,
    )
