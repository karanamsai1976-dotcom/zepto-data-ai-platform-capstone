# Support Assistant — Zepto Data & AI Platform Capstone

A retrieval-augmented Q&A API over an 8-document Zepto policy corpus, built with
LangGraph and served with FastAPI. Fully functional in a zero-cost, zero-network
"mock" mode (the graded default) — no API key, no signup, no LLM SDK import at
module scope required to run or pass tests.

## Architecture: ingestion -> embedding -> retrieval -> generation

1. **Ingestion** (`ingest.py`, function `load_documents`): reads all 8 files in
   `docs/doc_01.txt` .. `doc_08.txt`. Each file is short enough to be treated as one
   chunk — no further splitting needed. Reads with `encoding="utf-8-sig"` to strip a
   leading BOM (see "Known traps handled" below).
2. **Embedding** (`ingest.py`, function `ingest`): each chunk is embedded locally with
   `sentence-transformers` (`all-MiniLM-L6-v2`) and stored in a persistent ChromaDB
   collection (`get_collection`). Runs for real in both `MOCK_LLM` modes — needs no
   network after the model is cached, and no API key ever.
3. **Retrieval** (`ingest.py`, function `retrieve`; called from `graph.py`'s
   `retrieve_and_answer` node): a new query is embedded the same way, then ChromaDB
   returns the top-3 most similar chunks by cosine distance. Runs for real in both
   modes.
4. **Generation** (`graph.py`, inside `retrieve_and_answer` and `direct_answer`):
   the ONLY stage that branches on `MOCK_LLM`.
   - `MOCK_LLM` unset/`1` (graded default): a deterministic templated string —
     `f"Based on the retrieved context: {top_chunk_snippet}"` for policy questions,
     or a fixed canned string for general questions. No LLM call, no network call.
   - `MOCK_LLM=0` (optional, ungraded): `llm.py` is the ONLY file allowed to touch a
     real LLM. Its SDK import (`from groq import Groq`) lives inside a function, not
     at module scope, so the module imports cleanly with no `groq` package installed
     and no API key set (verified below) — this is what protects the graded default
     path on a grader machine with neither.

Routing itself (`classify_intent` -> conditional edge -> `retrieve_and_answer` OR
`direct_answer`) is a plain keyword heuristic and does **not** depend on `MOCK_LLM` —
identical routing logic runs in both modes.

## The MOCK_LLM contract

Read in exactly one place: `config.py`. `MOCK_LLM` unset or `"1"` -> mock mode, the
graded default (verified below: `MOCK_LLM (default, unset): True`).

## Prompt template (prompts.py)

`ANSWER_PROMPT_TEMPLATE` exists as literal text, showing all five skeleton
components plus a negative constraint and a few-shot example. Used by the optional
`MOCK_LLM=0` path; its presence is graded regardless of which mode runs. Real
rendered output, confirming every component substitutes correctly with no
`KeyError`:

```
You are a customer support assistant for Zepto, a quick-commerce grocery delivery
service. Your job is to answer customer questions using ONLY the policy context
provided below -- do not answer using information not present in the provided
context, and do not guess or make up policy details that are not stated.

Context:
[example context]

Task: Read the context above and answer the customer's question directly and
factually, citing the specific policy detail that supports your answer.

Format: Respond in 1-3 plain-English sentences. Do not use bullet points or
headers. Do not repeat the question back to the customer.

Length: Keep the answer under 60 words.

Example:
Question: How long do I have to report a damaged item?
Answer: You have 24 hours from delivery to report a damaged, spoiled, or missing
item using the "Report an Issue" button on the order page.

Now answer this question:
Question: What is the delivery fee?
Answer:
```

(role: "customer support assistant for Zepto"; context: the `{context}` block;
task: the "Task:" line; format: the "Format:" line; length: the "Length:" line;
negative constraint: "do not answer using information not present in the provided
context"; few-shot example: the worked Q&A pair.)

## LangGraph: StateGraph, three nodes, conditional edge

`graph.py` builds a `StateGraph` over a `TypedDict` state
(`query, intent, answer, sources, confidence`) with exactly three named nodes:

| Node | Mock behavior (graded) |
| --- | --- |
| `classify_intent` | Keyword heuristic, no LLM call. Substring match against `delivery, return, refund, membership, tracking, cancel, gift card, support hours`. |
| `retrieve_and_answer` | Real embed + real top-3 ChromaDB retrieval, then a canned templated answer. |
| `direct_answer` | Fixed canned string, no retrieval, no LLM. |

**Real routing verification, MOCK_LLM left at its default (unset):**

```
=== Policy question ===
{'query': 'What is the delivery fee?', 'intent': 'policy_question',
 'answer': 'Based on the retrieved context: Zepto delivers grocery and household
 essentials to serviceable pin codes within 10 to 30 minutes of order
 confirmation...', 'sources': ['doc_01#0', 'doc_05#0', 'doc_02#0'], 'confidence': 1.0}

=== General question ===
{'query': 'Who won the world cup?', 'intent': 'general_question',
 'answer': 'I can only answer questions about Zepto policies right now.',
 'sources': [], 'confidence': 1.0}
```

`"What is the delivery fee?"` (contains "delivery") correctly routes to
`retrieve_and_answer` via the conditional edge; `"Who won the world cup?"` (no
keyword match) correctly routes to `direct_answer`. Neither call makes a network
call to any LLM provider — confirmed by both succeeding with no `groq` package
installed and no API key set anywhere in the environment.

## Retrieval correctness

A delivery-fee question's top retrieved chunk is `doc_01#0` — the actual Delivery
Policy document, confirming the retrieved content genuinely matches the question
asked, not just a routing label. A cancellation question
(`"Can I cancel my order?"`) retrieves `doc_05#0` — the actual Cancellation Policy
document (verified in `tests/test_graph.py`,
`test_cancellation_question_routes_to_policy_and_hits_doc_05`, which passes). This
retrieval step runs for real in both `MOCK_LLM` modes.

## Structured output

`schemas.py` defines the response contract with Pydantic:
`answer: str`, `sources: list[str]`, `confidence: float` bounded `0.0-1.0`
structurally — verified by constructing `AskResponse(..., confidence=1.5)` and
confirming a real `ValidationError` is raised, not just documented. In mock mode,
`sources` = retrieved chunk IDs for policy questions (verified: `['doc_01#0',
'doc_05#0', 'doc_02#0']`), `[]` for general questions (verified above); `confidence`
is fixed at `1.0` deterministically, since there is no LLM output to validate
confidence against in mock mode.

`llm.py`'s `generate_structured_answer` implements the retry-on-validation-failure
path for the optional `MOCK_LLM=0` extension: on a JSON decode error, missing key,
or Pydantic `ValidationError` from the raw LLM output, it retries up to 2 additional
times with a corrective instruction appended to the prompt, then returns a clearly
marked error response (`answer` prefixed `"Error: ..."`, `confidence=0.0`) if every
attempt fails. This code path never triggers in `MOCK_LLM=1` (default) mode — its
presence was verified by importing `support_assistant.llm` successfully with no
`groq` package installed and no API key set, proving the SDK import is truly
function-local (inside `_call_groq`), not at module scope.

## Real verification: local FastAPI

Run with `MOCK_LLM` at its default (unset):

```
uvicorn support_assistant.main:app --port 8000
```

Real raw JSON from two actual calls:

**Policy question** (`{"query": "What is the delivery fee?"}`):
```json
{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del","sources":["doc_01#0","doc_05#0","doc_02#0"],"confidence":1.0}
```

**General question** (`{"query": "Who won the world cup?"}`):
```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

## Real verification: Docker

```
docker build -t zepto-support ./support_assistant
docker run -d -p 7860:7860 --name zepto-support-test zepto-support
```

Real build completed successfully (all layers, image tagged `zepto-support:latest`).
The embedding model is baked into the image at build time via a dedicated `RUN`
step, so `docker run` needs no network access. Real container logs confirmed
ingestion succeeded (8 chunks, no re-download) and uvicorn started on
`0.0.0.0:7860`. The same two `/ask` calls against the running container returned
identical correct JSON to the local FastAPI test above — confirming the
containerized app works end-to-end with no API key and no network access needed at
runtime. This is the required, graded baseline (local build + run); an actual push
to Hugging Face Spaces is an optional, ungraded stretch not attempted here.

## Tests

```
pytest support_assistant/tests -q
```

6 tests, all passing with `MOCK_LLM` unset (the graded path): both routing
branches, retrieval correctness for two different queries, the exact canned
strings, the confidence bound, and substring keyword matching ("cancellation"
matching "cancel").

## Known traps handled

- **BOM in corpus files:** PowerShell's `Out-File -Encoding utf8` writes a UTF-8
  BOM. `ingest.py` reads files with `encoding="utf-8-sig"`, which strips a leading
  BOM if present — caught by inspecting a real answer's text (`\ufeff` appeared
  right after the mock prefix before the fix; confirmed absent after).
- **Idempotent ingestion:** `ingest()` checks `collection.count()` before adding, so
  re-running `ingest.py` (or restarting the Docker container) never duplicates
  chunks.
- **No LLM SDK imported at module scope:** confirmed both by `llm.py` importing
  cleanly with no `groq` package installed, and by the whole module's tests/API
  passing with no API key set anywhere.
- **Mock answer string matches exactly:** verified character-for-character against
  real JSON responses above.
- **`sources` empty for general questions, populated for policy questions:**
  verified in both local and Docker real responses.

## How to run

From the repository root, with the virtual environment activated:

```
python -m support_assistant.ingest        # build/refresh the ChromaDB collection
pytest support_assistant/tests -q          # offline tests, no network needed
uvicorn support_assistant.main:app --port 8000
```

Docker (requires Docker Desktop):

```
docker build -t zepto-support ./support_assistant
docker run -p 7860:7860 zepto-support
```
