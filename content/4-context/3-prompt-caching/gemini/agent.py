from pathlib import Path
from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
client = genai.Client()

# Gemini caching creates a named server-side resource with explicit lifecycle
# create once, reference across many requests, delete when done
# note: cached content must be >= 1024 tokens

KNOWLEDGE_BASE = Path("knowledge_base.txt").read_text()  # ~4100 tokens

# step 1: create a named cache with explicit TTL
cache = client.caches.create(
    model=LLM_MODEL,
    config=types.CreateCachedContentConfig(
        system_instruction=KNOWLEDGE_BASE,
        ttl="300s",  # 5-minute TTL — extend with client.caches.update()
    ),
)
print(f"Cache created: {cache.name}")

# step 2: reference the cache — no need to resend the prompt
r1 = client.models.generate_content(
    model=LLM_MODEL,
    contents="I keep getting 429 errors. What should I do?",
    config=types.GenerateContentConfig(cached_content=cache.name),
)
print(r1.text)
print(f"Cached tokens: {r1.usage_metadata.cached_content_token_count}")
# -> Cached tokens: 4182

# same cache, different question — cached tokens reused
r2 = client.models.generate_content(
    model=LLM_MODEL,
    contents="How do I fix SSO login failures?",
    config=types.GenerateContentConfig(cached_content=cache.name),
)
print(r2.text)
print(f"Cached tokens: {r2.usage_metadata.cached_content_token_count}")
# -> Cached tokens: 4182

# step 3: cleanup — delete when done, or let TTL expire
client.caches.delete(name=cache.name)
