from pathlib import Path
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

LLM_MODEL = "gpt-5.4"
model = ChatOpenAI(model=LLM_MODEL)

# OpenAI caching is automatic — no cache_control needed
# identical prefixes >= 1024 tokens are cached and reused
# static content (instructions, examples) should go first for best hit rate

KNOWLEDGE_BASE = Path("knowledge_base.txt").read_text()  # ~4100 tokens

system = SystemMessage(content=KNOWLEDGE_BASE)

agent = create_agent(model, tools=[])

# request 1: cold cache — prompt is processed and cached automatically
result = agent.invoke({
    "messages": [system, ("user", "I keep getting 429 errors. What should I do?")],
})
ai_msg = result["messages"][-1]
print(ai_msg.content)
usage = ai_msg.response_metadata["token_usage"]
print(f"Cached tokens: {usage['prompt_tokens_details']['cached_tokens']}")
# -> Cached tokens: 0 (cache miss — prefix is now stored)

# request 2: warm cache — identical prefix served from cache
result = agent.invoke({
    "messages": [system, ("user", "How do I fix SSO login failures?")],
})
ai_msg = result["messages"][-1]
print(ai_msg.content)
usage = ai_msg.response_metadata["token_usage"]
print(f"Cached tokens: {usage['prompt_tokens_details']['cached_tokens']}")
# -> Cached tokens: 2816 (cache hit — lower cost, lower latency)
