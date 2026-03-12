from pathlib import Path
import anthropic

LLM_MODEL = "claude-opus-4-6"
client = anthropic.Anthropic()

# prompt caching requires explicit opt-in via cache_control breakpoints
# marks a prefix boundary — everything up to this point is cached
# 25% surcharge on cache writes, 90% discount on cache reads, 5-min TTL

KNOWLEDGE_BASE = Path("knowledge_base.txt").read_text()  # ~4100 tokens

# cache_control breakpoint on the system block — up to 4 breakpoints allowed
system = [{
    "type": "text",
    "text": KNOWLEDGE_BASE,
    "cache_control": {"type": "ephemeral"},  # 5-min TTL, refreshed on each hit
}]

# request 1: cache write — prompt stored, surcharge applies
r1 = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, system=system,
    messages=[{"role": "user", "content": "I keep getting 429 errors. What should I do?"}],
)
print(r1.content[0].text)
print(f"Cache write: {r1.usage.cache_creation_input_tokens} tokens")
print(f"Cache read:  {r1.usage.cache_read_input_tokens} tokens")
# -> Cache write: 4182 tokens, Cache read: 0 tokens

# request 2: cache hit — prefix served from cache at 90% discount
r2 = client.messages.create(
    model=LLM_MODEL, max_tokens=1024, system=system,
    messages=[{"role": "user", "content": "How do I fix SSO login failures?"}],
)
print(r2.content[0].text)
print(f"Cache write: {r2.usage.cache_creation_input_tokens} tokens")
print(f"Cache read:  {r2.usage.cache_read_input_tokens} tokens")
# -> Cache write: 0 tokens, Cache read: 4182 tokens
