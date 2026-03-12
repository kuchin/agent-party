# Agent Party — The Plan

## What this is

A side-by-side code comparison site for AI agent frameworks, modeled after [component.party](https://component.party) (which does the same thing for frontend frameworks like React, Vue, Svelte, etc.).

Component.party works because it shows the exact same task implemented across multiple frameworks, one tiny example per concept. You pick a concept — "declare state," "update state," "computed property" — and instantly see how React, Vue, Svelte, Solid, Angular each handle it. 5-15 lines per panel. No prose. No opinions. Just code.

Nothing like this exists for AI agent frameworks. The landscape is fragmented — LangGraph, Pydantic AI, OpenAI Agents SDK, Google ADK, CrewAI, Mastra, Agno, smolagents — and every developer evaluating them has to read five blog posts, three quickstarts, and two GitHub repos before they can compare approaches. The closest thing is a single Arize AI blog post from late 2024 that builds one agent in three frameworks, but it's frozen in time and only covers three of them.

Agent Party solves this by defining a canonical set of patterns that span the full surface area of what an agent framework does, then implementing each pattern in every framework using minimal, runnable code.

---

## The frameworks (initial scope)

Start with three that represent genuinely different philosophies and languages:

**LangGraph** (Python) — Graph-based state machine. The most established framework in the ecosystem. Agents are modeled as directed graphs with nodes, edges, and shared state. Built on top of LangChain. Offers both a high-level `create_react_agent` shortcut and a low-level `StateGraph` API for full control. State persistence via checkpointers. Heaviest abstraction layer of the three.

**Pydantic AI** (Python) — Type-safe, decorator-driven. Built by the Pydantic team (the validation layer underneath OpenAI SDK, Anthropic SDK, LangChain, and most of the Python AI ecosystem). Designed to bring the "FastAPI feeling" to agent development. First-class dependency injection via typed `RunContext[T]`. Tools registered via decorators. Lightest abstraction — feels like writing normal Python functions.

**Mastra** (TypeScript) — TypeScript-first, batteries-included. From the team behind Gatsby. Agents, tools, workflows, memory, evals all in one framework. Tools defined via `createTool()` factories with Zod schemas. Built on Vercel AI SDK internally, integrates natively with Next.js/React. The clear choice for TypeScript/Node teams.

Future additions could include OpenAI Agents SDK, Claude Agent SDK, Google ADK, CrewAI, Agno, smolagents, and others. The pattern taxonomy is framework-agnostic by design.

Recommended next additions:

- **OpenAI Agents SDK** — The highest-value first-party addition. It adds a real orchestration layer on top of the raw OpenAI SDK: tools, handoffs, tracing, sessions, and streaming. This is meaningfully different from both the native OpenAI SDK examples and the meta-frameworks already covered.
- **Claude Agent SDK** — Anthropic's first-party agent framework. It exposes the same agent loop, built-in tools, permissions, sessions, hooks, and subagents that power Claude Code, so it would add a strong provider-native counterpart to OpenAI Agents SDK rather than just another raw Messages API wrapper.
- **LlamaIndex** — The strongest non-provider framework gap. It has a distinct “agents over data” flavor, with workflows, tools, memory, and retrieval patterns that would add a different mental model than LangGraph, Pydantic AI, or Mastra.
- **Google ADK** — The best provider-native counterpart to OpenAI Agents SDK. Google positions it as a modular agent framework, optimized for Gemini but not limited to it, and it would broaden the comparison set beyond raw provider SDK usage.

Good follow-up additions if the site grows into more multi-agent/orchestration scenarios:

- **CrewAI** — Especially valuable if the site adds explicit delegation, crews, or flow-based orchestration patterns.
- **AutoGen** — Strong fit if the site wants to compare multi-agent team patterns directly.
- **Semantic Kernel** — Most useful if the comparison expands toward enterprise orchestration and cross-language parity.

---

## The pattern taxonomy

Every agent framework answers the same set of questions. The taxonomy below defines 17 patterns organized into 6 levels. Each level addresses one fundamental question about how the framework works. Each pattern isolates exactly one concept and should be expressible in 5-15 lines of code per framework.

### Level 0 — The Call
*What is the minimum code to use this thing?*

**1. Hello world**
Prompt in, text out. The absolute minimum: initialize an agent, send a message, get a response. No tools, no configuration, no system prompt. This pattern reveals boilerplate cost — how many imports, how many lines before you get a response. LangGraph speaks in message dicts. Pydantic AI takes a string and returns a result object. Mastra instantiates a class and calls `.generate()`.

**2. Instructions**
Set a system prompt that defines the agent's persona, constraints, or behavior. This is still not an "agent" — it's a configured LLM call. But it shows how each framework models the concept of identity. Some frameworks treat instructions as a constructor parameter, others as a decorator, others as a message in the messages array.

### Level 1 — Tools
*What can this agent do beyond generating text?*

Tools are what turn an LLM into an agent. A tool is a function with a typed input schema that the LLM can decide to call. The framework's job is to: describe the tool to the LLM, parse the LLM's tool call request, execute the function, and return the result back to the LLM.

**3. Tool**
Define a single function with typed parameters that the LLM can call. This is the core primitive. The example should use a weather lookup or similar — something with at least one string parameter and a return value. This pattern reveals: how do you define the schema (decorators, factory functions, type hints)? How does the framework extract parameter descriptions (docstrings, Zod `.describe()`, Field descriptions)? How is the tool registered with the agent?

**4. Multi-step**
The ReAct loop: the agent calls a tool, observes the result, thinks about what to do next, and may call another tool or respond. This is the pattern that separates an "agent" from a "chat wrapper with function calling." The example should require at least two tool calls to answer the question (e.g., "compare the weather in Paris and Tokyo"). Key differences: LangGraph's graph naturally loops between the LLM node and the tool node. Pydantic AI loops internally. Mastra requires explicit `maxSteps` (defaults to 1, which means no looping).

**5. Multi-tool choice**
The agent has access to multiple tools and must decide which one(s) to call. The example should give the agent 2-3 tools (e.g., weather, calculator, web search) and ask a question that requires picking the right one. This demonstrates tool routing — the LLM's ability to select, and the framework's ability to present multiple tools cleanly.

**6. Tool error handling**
A tool throws an exception. What happens? Does the agent see the error and retry? Does it fall back to another tool? Does the framework crash? This pattern reveals production-readiness. LangGraph has middleware for wrapping tool errors. Pydantic AI has configurable retries. Mastra surfaces errors back to the model.

### Level 2 — Output
*What shape does the agent's final answer take?*

**7. Structured output**
The agent returns typed, validated data instead of free-form text. In Python: a Pydantic BaseModel. In TypeScript: a Zod schema. The framework instructs the LLM to respond in a specific JSON shape and validates the result. Pydantic AI does this via `output_type` on the agent. LangGraph uses `response_format` on `create_react_agent`. Mastra passes a Zod schema via the `output` option at generate-time.

**8. Tool-as-output**
An alternative to native structured output: you define a "tool" whose real purpose is to enforce output structure. The LLM is instructed (via prompt or configuration) to always call this tool as its final action. The tool's input schema IS the output schema. This is a real production pattern used when native structured output is unreliable, when you need the output contract to live in the tool definition rather than the output API, or when the model provider doesn't support structured output natively. Different mechanism, same goal as pattern 7.

### Level 3 — Context
*How does runtime state enter the agent?*

**9. Runtime context**
How runtime data — a database connection, the current user, a config object, an API client — reaches the agent's instructions and tools. This is one question viewed from two angles: "how does runtime state reach the system prompt" and "how does runtime state reach the tools." In well-designed frameworks, the answer is the same mechanism.

Pydantic AI makes this most explicit: you declare a `deps_type` (a dataclass or similar), pass an instance at runtime, and both `@agent.instructions` and `@agent.tool` receive it via typed `RunContext[Deps]`. LangGraph passes runtime data through `RunnableConfig["configurable"]` — functional but untyped. Its nodes also receive the graph `state` and a `config` object. Mastra supports async instruction functions that resolve at runtime and tools that close over external dependencies via factory patterns.

This single pattern tells you more about a framework's production philosophy than any feature list.

**10. Conversation state / persistence**
How the framework handles multi-turn conversations and where it believes state lives. This is not just "pass prior messages" — it's one of the deepest philosophical differences between frameworks.

LangGraph persists checkpoints to threads via checkpointers. You configure a storage backend (in-memory, SQLite, Postgres), and every invocation automatically saves and restores state by thread ID. State lives in the infrastructure.

Pydantic AI expects you to pass `message_history` into each run and can process that history before each request via history processors. State lives in your application — you own it, you persist it, you pass it in.

Mastra uses a memory system identified by `resourceId` and `threadId`, backed by configurable storage providers. It also supports observational memory — background agents that compress conversation history into dense observation logs to keep the context window small while preserving long-term recall. State lives in the framework's storage layer.

**11. RAG (retriever as tool)**
Vector search exposed as a tool the agent can call. RAG is not a special agent primitive — it's a tool pattern. But it's the single most common "real" tool people build, and the ergonomics differ meaningfully between frameworks. Some have built-in retriever tools or knowledge base abstractions. Some make you wire the vector store, embedding model, and retrieval logic yourself. This pattern shows the full path: embed documents, create a retriever, expose it as a tool, let the agent decide when to search.

### Level 4 — Interaction / Observability
*How do you watch the agent work?*

Streaming is not about the output contract. It's about the runtime experience — the relationship between the caller and the running agent.

**12. Streaming (text)**
Token-by-token text output as the agent generates its response. Table stakes for any agent that faces a user. The example should show how to consume the stream. LangGraph streams via `.stream()` or `.astream()` with configurable stream modes. Pydantic AI has `agent.run_stream()` returning an async iterable. Mastra has `agent.stream()` returning a text stream.

**13. Stream events (lifecycle)**
Observing the full execution lifecycle in real-time: tool calls being made, tool results coming back, thinking/reasoning tokens, intermediate steps. This is what you need to build an agent UI that shows "Searching for weather data..." → "Processing results..." → "Generating response...". LangGraph streams events via `stream_mode="updates"` or `stream_mode="messages"`. Pydantic AI has `run_stream_events()` emitting typed event objects (`FunctionToolCallEvent`, `FunctionToolResultEvent`, `PartDeltaEvent`). Mastra exposes text, structured objects, tool calls, reasoning, and a full chunk stream.

### Level 5 — Orchestration
*How do you compose agents into larger systems?*

**14. Subagents**
One agent delegates a subtask to another agent. The parent agent calls the child agent as if it were a tool. This pattern reveals whether the framework treats agents as composable, first-class units. LangGraph composes agents as subgraphs within a parent graph. Pydantic AI allows calling one agent from within another agent's tool. Mastra registers agents with a shared Mastra instance and can call them from tools or workflows.

**15. Graph / workflow**
Explicit control flow with branching, conditions, and routing. When you need deterministic orchestration — not just "let the LLM decide" but "if condition X, go to step Y" — how does the framework model this?

This is where the frameworks diverge most dramatically. LangGraph IS a graph — `StateGraph` with `add_node()`, `add_edge()`, `add_conditional_edges()`. The entire framework identity is built around explicit graph construction. Mastra has a separate workflow engine with an intuitive chaining syntax: `.then()`, `.branch()`, `.parallel()`. Steps have typed input/output schemas. Pydantic AI recently added graph support via type hints and dataclasses, modeling nodes as dataclass types and edges as union return types.

### Level 6 — Intervention / Policy
*How do you control what the agent does?*

These patterns are about interception — inspecting and modifying the agent's behavior at defined points in execution. They are distinct from orchestration (which is about routing and composition).

**16. Human-in-the-loop**
Pause the agent's execution at a defined point, surface information to a human, wait for approval or modification, then resume. This is temporal interception — the agent stops, a human decides, the agent continues.

LangGraph models this via interrupts — explicit pause/resume points in the graph. The agent's state is checkpointed, execution halts, and resumes when the human responds. The docs show interrupting before tool execution to let a human review what the agent is about to do. Pydantic AI supports tool-level approval flags where specific tool calls require human confirmation before proceeding. Mastra uses its workflow suspend/resume mechanism — execution pauses, state persists to storage, and resumes when input arrives.

**17. Schema Guided Reasoning**
TBD

**18. Guardrails**
Validate, filter, or reject the agent's input or output before it passes through. This is evaluative interception — you inspect the data and decide whether to allow, modify, or block it.

LangGraph implements this via middleware — composable functions that wrap model calls or tool executions. Pydantic AI uses output validators and tool-level validation. Mastra has explicit input and output processors — functions that run before the prompt reaches the model and after the response comes back.

---

## Design principles for the code examples

Each pattern should follow these rules:

**Minimal.** 5-15 lines per framework. Strip everything that isn't demonstrating the specific concept. No imports that aren't necessary. No error handling unless the pattern IS error handling. No comments unless they clarify a framework-specific concept.

**Runnable.** Every example should be copy-pasteable and executable with only an API key as setup. Use mock data where possible (hardcoded weather responses, fake database objects) to eliminate external dependencies.

**Same task.** All frameworks solve the identical problem in each pattern. Same prompt, same tool behavior, same expected output. The ONLY thing that changes is the framework's API.

**Honest.** If a framework doesn't support a pattern natively, show the idiomatic workaround — don't hide the gap. If one framework needs 3 lines and another needs 15, that's information. Don't normalize line counts.

**Current.** Pin to latest stable versions. Agent frameworks move fast — examples that are 6 months old may use deprecated APIs. Each example should include the framework version it was tested against.

---

## Site structure

The site should look and work like component.party:

- Left sidebar: list of all 17 patterns, grouped by level
- Main area: code panels side-by-side (or tabbed on mobile) for each selected framework
- Top bar: framework selector (check/uncheck which frameworks to compare)
- Each pattern has a one-line description visible above the code panels
- No prose, no blog post, no opinions. Just code.

Optional additions: line count per example, link to each framework's relevant docs, "copy" button per panel, syntax highlighting matched to language.

---

## What this is NOT

This is not a benchmark. It doesn't measure performance, latency, or token usage. It doesn't rank frameworks. It doesn't recommend one over another. It's a reference — a place to see how each framework models the same concept, so you can make your own informed decision about which one fits your mental model and your stack.

---

4 additional context/memory patterns worth adding:

**Best Additions**
1. `Dynamic Instructions` or `Runtime Prompt`
This is the biggest gap. Your current `runtime context` examples mostly show how app state reaches tools, but the docs for Pydantic AI, LangGraph, Mastra, and AI SDK all also emphasize shaping the prompt/instructions from runtime context. That is a distinct pattern and a good comparison axis.
Sources: [Pydantic dependencies](https://ai.pydantic.dev/dependencies/), [LangChain dynamic prompt](https://docs.langchain.com/oss/python/langchain-agents), [LangChain context overview](https://docs.langchain.com/oss/python/concepts/context), [Mastra runtime context](https://mastra.ai/docs/agents/runtime-context), [AI SDK call options](https://ai-sdk.dev/docs/agents/configuring-call-options)

2. `History Compaction` or `Context Pruning`
This is the next strongest one. Current docs increasingly treat “how do you keep history useful and bounded?” as first-class:
- Pydantic AI: `history_processors`
- LangGraph/LangChain: trim/delete/summarize middleware
- AI SDK: `pruneMessages`
- Mastra: memory processors / working memory
This would be a very good full-matrix scenario.
Sources: [Pydantic message history](https://ai.pydantic.dev/message-history/), [LangChain short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory), [AI SDK pruneMessages](https://ai-sdk.dev/docs/reference/ai-sdk-ui/prune-messages), [Mastra working memory example](https://mastra.ai/en/examples/memory/streaming-working-memory), [Mastra memory processors](https://mastra.ai/blog/changelog-2025-04-02)

**Good Advanced Additions**
3. `Long-term Memory` or `Cross-thread Recall`
Your current memory panel is short-term only. Docs now expose stronger long-term patterns:
- LangGraph store / namespaces / semantic search
- Mastra working memory + semantic recall
- AI SDK memory page
- Pydantic AI `MemoryTool` exists, but is Anthropic-specific
This is important, but less clean as a universal matrix because raw OpenAI/Anthropic/Gemini have weaker native stories.
Sources: [LangChain long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory), [AI SDK memory](https://ai-sdk.dev/docs/agents/memory), [Pydantic built-in tools](https://ai.pydantic.dev/builtin-tools/), [Mastra semantic recall / working memory](https://mastra.ai/en/examples/memory/streaming-working-memory), [Mastra cross-thread recall](https://mastra.ai/blog/changelog-2025-06-13)

4. `Prompt Caching` / `Context Caching`
This is very current across providers:
- OpenAI prompt caching
- Anthropic prompt caching
- Gemini context caching
Useful, but I would not make it a main 7-framework matrix first, because the abstraction layers expose it unevenly.
Sources: [OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching/overview), [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching), [Gemini context caching](https://ai.google.dev/gemini-api/docs/caching/)
