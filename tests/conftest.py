import os

# Importing gtm_agent constructs chat models at module scope, which requires a
# provider key to be present even though the tests never call out to a model.
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"
