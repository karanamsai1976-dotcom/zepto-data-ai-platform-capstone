"""Configuration for the support_assistant module. MOCK_LLM is read HERE, in
exactly one place -- every other module imports this constant rather than
reading the environment variable itself."""

import os
from pathlib import Path

MOCK_LLM = os.environ.get("MOCK_LLM", "1") != "0"

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3

POLICY_KEYWORDS = [
    "delivery", "return", "refund", "membership", "tracking",
    "cancel", "gift card", "support hours",
]
