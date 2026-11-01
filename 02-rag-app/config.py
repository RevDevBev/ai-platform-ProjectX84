import os

CANDIDATES = 20
TOP_N = 3

# Placeholder: you will set this from real data in Step 5.
REFUSAL_THRESHOLD = float(os.environ.get("RAG_REFUSAL_THRESHOLD", "-2.11"))

REFUSAL_TEXT = "I don't know based on the provided documents."