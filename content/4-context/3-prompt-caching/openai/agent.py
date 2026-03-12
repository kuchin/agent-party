from pathlib import Path
from openai import OpenAI

LLM_MODEL = "gpt-5.4"
client = OpenAI()

# prompt caching is automatic — no opt-in, no code changes
# any prefix >= 1024 tokens is cached on first request, reused on subsequent ones
# static content (instructions, examples) should go first for best hit rate

KNOWLEDGE_BASE = Path("knowledge_base.txt").read_text()  # ~4100 tokens

# request 1: cold cache — prompt is processed and cached automatically
r1 = client.responses.create(
    model=LLM_MODEL,
    instructions=KNOWLEDGE_BASE,
    input="I keep getting 429 errors. What should I do?",
)
print(r1.output_text)
cached_1 = r1.usage.input_tokens_details.cached_tokens
print(f"Cached tokens: {cached_1}")
# -> Cached tokens: 0 (cache miss — prefix is now stored)

# request 2: warm cache — identical instruction prefix served from cache
r2 = client.responses.create(
    model=LLM_MODEL,
    instructions=KNOWLEDGE_BASE,
    input="How do I fix SSO login failures?",
)
print(r2.output_text)
cached_2 = r2.usage.input_tokens_details.cached_tokens
print(f"Cached tokens: {cached_2}")
# -> Cached tokens: 3328 (cache hit — lower cost, lower latency)
