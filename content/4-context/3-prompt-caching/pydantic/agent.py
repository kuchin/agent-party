from pathlib import Path
from pydantic_ai import Agent

LLM_MODEL = "openai:gpt-5.4"

# prompt caching is automatic with OpenAI — no extra settings needed
# any prefix >= 1024 tokens is cached on first request, reused on subsequent ones
# static content (instructions, examples) should go first for best hit rate

KNOWLEDGE_BASE = Path("knowledge_base.txt").read_text()  # ~4100 tokens

agent = Agent(LLM_MODEL, instructions=KNOWLEDGE_BASE)

# request 1: cold cache — prompt is processed and cached automatically
result = agent.run_sync("I keep getting 429 errors. What should I do?")
print(result.output)
print(f"Usage: {result.usage()}")
# -> cache_read_tokens = 0 (cache miss — prefix is now stored)

# request 2: warm cache — identical instruction prefix served from cache
result = agent.run_sync("How do I fix SSO login failures?")
print(result.output)
print(f"Usage: {result.usage()}")
# -> cache_read_tokens = 2816 (cache hit — lower cost, lower latency)
