# Coverage Map

Last reviewed: 2026-03-11

## Scope and method

- I compared the current scenario inventory under `content/` against the current official docs for each framework/provider on 2026-03-11.
- Status meanings:
  - `Covered`: the repo has a dedicated example that matches a first-class docs pattern.
  - `Partial`: the repo has a simplified or manual version, but not the richer or more native docs surface.
  - `Missing`: the docs expose the capability and the repo has no dedicated example for it yet.
- Important: `openai`, `anthropic`, and `gemini` in this repo are provider SDK tracks, not full agent-framework tracks. Their current docs now include adjacent agent platforms, hosted tools, and realtime products. I count that surface as uncovered here, but some of it may deserve separate framework tracks instead of being folded into the current provider examples.

## Repo-wide summary

- Current taxonomy size: 22 scenarios across Basics, Tools, Output, Streaming, Context, Memory, RAG, and Agents.
- Current panel parity: all 7 frameworks cover all 22 current scenarios.
- The main gap is not missing panels inside the current taxonomy. The main gap is that the taxonomy itself stops short of major docs surfaces that now matter.
- Cross-framework gaps:
  - workflow/orchestration
  - human-in-the-loop, approval, interrupt-resume
  - guardrails, processors, middleware policy
  - provider-native hosted tools, files, MCP, and code execution
  - realtime, voice, multimodal UI
  - evals, tracing, observability, deployment
- Cross-framework RAG note: current RAG examples mostly compare app-level retrieval patterns. Several tracks still use Chroma/Vectra plus OpenAI embeddings instead of each framework or provider's native retrieval, file, or vector features.

## Quick map

| Framework | Current scenario coverage | Biggest uncovered docs areas |
| --- | --- | --- |
| OpenAI | 22/22 | built-in tools, remote MCP, background mode, Realtime API, Agents SDK/ChatKit |
| Anthropic | 22/22 | server-side tools, citations/files, extended thinking, MCP, Agent SDK/Skills, batch |
| Gemini | 22/22 | Google Search/URL Context/Code Execution/File Search, Files API, Live API, native embeddings, batch |
| Pydantic AI | 22/22 | built-in tools/toolsets, MCP, deferred tools/HITL, graphs, durable execution, evals |
| LangGraph | 22/22 | low-level graphs, workflows, interrupts, subgraphs, long-term memory, Studio/deploy |
| AI SDK | 22/22 | UI layer, message persistence/resume streams, MCP, middleware, workflow patterns, multimodal/testing |
| Mastra | 22/22 | workflows, suspend/resume approvals, processors/guardrails, native RAG surface, voice, observability/evals/MCP |

## OpenAI

Current track focus: raw Responses API patterns, not the newer first-party Agents/ChatKit surface.

| Area | Status | Notes |
| --- | --- | --- |
| Core Responses API | Covered | Basics, tools, structured output, streaming, and manual multi-step loops are all present. |
| Conversation state and compaction | Covered | `previous_response_id`, message history, and three history-compaction examples are covered. |
| Prompt caching | Covered | There is a warm/cold cache example, but only the basic automatic path. |
| Retrieval / RAG | Partial | RAG examples use local Chroma plus OpenAI embeddings, not the native File Search tool. |
| Built-in tools and remote MCP | Missing | No web search, file search, remote MCP, code interpreter, computer-use, or image-generation tool examples. |
| Long-running and async execution | Missing | No background mode or webhook-driven completion examples. |
| Realtime / voice / multimodal agents | Missing | No Realtime API, voice-agent, speech, or multimodal session examples. |
| Agents platform | Missing | No Agents SDK, ChatKit, shell/skills, agent evals, or trace grading coverage. |

Recommended next additions:

1. Built-in tools: web search, file search, remote MCP.
2. Background mode plus webhooks.
3. A separate OpenAI Agents SDK or ChatKit track.

Docs used: [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state), [Using tools](https://developers.openai.com/api/docs/guides/tools), [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), [Background mode](https://developers.openai.com/api/docs/guides/background), [Realtime API](https://developers.openai.com/api/docs/guides/realtime)

## Anthropic

Current track focus: raw Messages API plus client-side tools.

| Area | Status | Notes |
| --- | --- | --- |
| Core Messages API, tool use, structured output, streaming | Covered | The repo covers the basic Claude call loop well. |
| Context management | Partial | Prompt caching and history compaction are present, but context editing and token-counting patterns are not isolated. |
| Server-side tools and citations | Missing | No web search, web fetch, code execution, search-results citations, memory, bash, computer use, or text editor examples. |
| Files / PDF / vision | Missing | No Files API or PDF-grounded answer flows. |
| Advanced reasoning modes | Missing | No extended thinking, adaptive thinking, or effort-control examples. |
| MCP, Agent Skills, Agent SDK | Missing | None of the newer Anthropic agent-platform surfaces are represented. |
| Batch processing and evaluation / guardrails | Missing | No batch jobs, eval flows, or docs-backed guardrail patterns. |

Recommended next additions:

1. Search results or web search with citations.
2. Extended thinking with tool use.
3. MCP connector or a separate Anthropic Agent SDK / Skills track.

Docs used: [Features overview](https://docs.anthropic.com/en/docs/build-with-claude/overview), [Tool use overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview), [Prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching), [Extended thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking), [Files API](https://docs.anthropic.com/en/docs/build-with-claude/files), [Batch processing](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)

## Gemini

Current track focus: basic GenAI SDK patterns, not Gemini's broader tools-and-agents surface.

| Area | Status | Notes |
| --- | --- | --- |
| Core text/chat/function calling/structured output/streaming | Covered | The base Gemini call loop is well represented. |
| Session state and context caching | Partial | Chat sessions and context caching are covered, but thought signatures and richer session-management patterns are not isolated yet. |
| Tool calling depth | Partial | Multi-step function calling is covered, but parallel and automatic compositional function-calling are not shown explicitly. |
| Native Gemini tools | Missing | No Google Search, URL Context, Google Maps, Code Execution, Computer Use, or File Search examples. |
| Files and native embeddings | Missing | Current RAG setup still uses OpenAI embeddings instead of Gemini embeddings, File Search, or Files API flows. |
| Live API / realtime voice-video | Missing | No Live API or realtime multimodal session examples. |
| Batch and long-context / thinking features | Missing | No Batch API, long-context, thinking, or thought-signature coverage. |

Recommended next additions:

1. Google Search plus URL Context plus Code Execution.
2. Native Gemini embeddings or File Search RAG instead of OpenAI embeddings.
3. Gemini Live API voice session example.

Docs used: [Function calling](https://ai.google.dev/gemini-api/docs/function-calling), [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output), [Context caching](https://ai.google.dev/gemini-api/docs/caching), [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search), [URL context](https://ai.google.dev/gemini-api/docs/url-context), [Code execution](https://ai.google.dev/gemini-api/docs/code-execution), [Files API](https://ai.google.dev/gemini-api/docs/files), [Live API](https://ai.google.dev/gemini-api/docs/live-api), [Embeddings](https://ai.google.dev/gemini-api/docs/embeddings), [Batch API](https://ai.google.dev/gemini-api/docs/batch-api)

## Pydantic AI

Current track focus: the core `Agent` API. That matches the current taxonomy well, but the current docs now extend far beyond single-agent basics.

| Area | Status | Notes |
| --- | --- | --- |
| Core single-agent patterns | Covered | Dependencies, dynamic instructions, function tools, output schemas, history, streaming, and basic subagents are all present. |
| Multi-agent delegation | Partial | The repo covers simple agent delegation, but not hand-off, deep-agent patterns, or multi-agent observability. |
| Toolsets, built-in tools, MCP | Missing | Current examples use only plain function tools. No toolsets, provider built-ins, or MCP client/server examples. |
| Deferred tools / human-in-the-loop | Missing | No approval-required or externally executed tool examples. |
| Graph control flow | Missing | No `pydantic-graph`, steps, joins/reducers, decisions, or parallel execution examples. |
| Durable execution | Missing | No Temporal, DBOS, or Prefect-backed durable runs. |
| Evals, UI event streams, A2A, testing | Missing | None of the newer integration surfaces are covered. |
| Multimodal, thinking, embeddings | Missing | No image/audio/video/document inputs, thinking controls, or native embeddings examples. |

Recommended next additions:

1. Deferred tool approval.
2. MCP client or built-in tools example.
3. Pydantic Graph or durable execution example.

Docs used: [Multi-agent patterns](https://ai.pydantic.dev/multi-agent-applications/), [Built-in tools](https://ai.pydantic.dev/builtin-tools/), [MCP client](https://ai.pydantic.dev/mcp/client/), [Deferred tools](https://ai.pydantic.dev/deferred-tools/), [Pydantic Graph](https://ai.pydantic.dev/graph/), [Durable execution](https://ai.pydantic.dev/durable_execution/overview/), [Pydantic Evals](https://ai.pydantic.dev/evals/)

## LangGraph

Current track focus: high-level LangChain `create_agent` patterns plus some LangGraph persistence and middleware. The repo barely touches the low-level LangGraph surface that the current docs emphasize.

| Area | Status | Notes |
| --- | --- | --- |
| High-level agent patterns | Covered | Basics, tools, output, streaming, dynamic prompt middleware, and tool-error middleware are present. |
| Short-term memory and checkpointed persistence | Covered | Message history, `thread_id`, checkpointers, and history compaction are represented well. |
| Middleware / guardrails | Partial | Some middleware usage is present, but not the broader guardrail, human-in-the-loop, or MCP middleware surfaces. |
| Low-level Graph API / Functional API / workflows | Missing | No explicit `StateGraph`, routing, parallel branches, orchestrator-worker, or evaluator-optimizer examples. |
| Interrupts / human-in-the-loop / time travel | Missing | No pause-resume or resume-from-checkpoint examples. |
| Subgraphs and true graph-based multi-agent systems | Partial | The repo has subagents, but not actual LangGraph subgraphs or parent-child graph composition. |
| Long-term memory / store | Missing | No store-backed long-term memory or cross-thread recall examples. |
| Studio, testing, deployment, observability | Missing | No LangSmith Studio, test, deployment, or observability coverage. |

Recommended next additions:

1. One real `StateGraph` workflow with branching or parallelism.
2. An interrupt / approval example.
3. Subgraphs or store-backed long-term memory.

Docs used: [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview), [Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents), [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs), [Middleware overview](https://docs.langchain.com/oss/python/langchain/middleware/overview), [Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory), [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)

## AI SDK

Current track focus: AI SDK Core plus `ToolLoopAgent`. The current docs cover much more than the current repo, especially AI SDK UI and the broader Core feature set. AI SDK 6 is the current docs line.

| Area | Status | Notes |
| --- | --- | --- |
| Core agent loop, tools, output, streaming, subagents | Covered | The repo covers the core TypeScript call loop well. |
| Runtime call configuration | Covered | Dynamic instructions and runtime-context examples cover the basic docs story here. |
| Memory | Partial | Current memory is only a manual `ModelMessage[]` store. Docs now describe provider-defined tools, memory providers, and custom-tool approaches. |
| Workflow patterns | Missing | No sequential, parallel, routing, evaluator-optimizer, or orchestration examples from the current docs. |
| AI SDK UI | Missing | No `useChat`, message persistence, resume streams, or generative UI examples. |
| MCP and middleware | Missing | No MCP tools, language-model middleware, guardrail, or middleware-based RAG examples. |
| Broader Core surface | Missing | No embeddings, reranking, image generation, video generation, speech, transcription, testing, telemetry, or provider-management examples. |

Recommended next additions:

1. `useChat` plus message persistence or resume streams.
2. MCP tools example.
3. Workflow patterns or middleware-backed guardrail/RAG example.

Docs used: [AI SDK docs](https://ai-sdk.dev/docs), [Agents](https://ai-sdk.dev/docs/agents), [Building agents](https://ai-sdk.dev/docs/agents/building-agents), [Workflow patterns](https://ai-sdk.dev/docs/agents/workflows), [Memory](https://ai-sdk.dev/docs/agents/memory), [MCP](https://ai-sdk.dev/docs/ai-sdk-core/mcp-tools), [Language model middleware](https://ai-sdk.dev/docs/ai-sdk-core/middleware), [AI SDK UI overview](https://ai-sdk.dev/docs/ai-sdk-ui/overview), [Chatbot message persistence](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence), [AI SDK Core](https://ai-sdk.dev/docs/ai-sdk-core)

## Mastra

Current track focus: core agent API usage. That covers the agent layer reasonably well, but Mastra's current docs are much broader than the repo's current taxonomy.

| Area | Status | Notes |
| --- | --- | --- |
| Core agent patterns | Covered | Agents, tools, structured output, streaming, runtime context, dynamic instructions, memory, and subagents are all present. |
| Native RAG surface | Partial | The repo has RAG examples, but they use local Vectra plus OpenAI embeddings instead of Mastra's broader chunking, embedding, vector, retrieval, reranking, and graph-RAG docs surface. |
| Workflows and orchestration | Missing | No `createWorkflow`, branch, parallel, loops, nested workflows, or workflow-as-step examples. |
| Supervisor / network / subworkflow composition | Partial | Subagents are covered, but agent networks, workflow tools, and supervisor controls are not. |
| Suspend/resume and approval | Missing | No human review, suspend/resume, or approval flows. |
| Processors / guardrails | Missing | No input processors, output processors, sanitization, or prompt-injection protection examples. |
| Voice | Missing | No speech-to-text, text-to-speech, or speech-to-speech examples. |
| Observability, evals, MCP, deployment | Missing | No tracing, scorers, MCP, Studio, auth, or deployment coverage. |

Recommended next additions:

1. One real Mastra workflow with branch or suspend/resume.
2. Agent-network or workflow-as-tool example.
3. Native Mastra RAG, voice, or observability/evals example.

Docs used: [Mastra home](https://mastra.ai/), [Agents overview](https://mastra.ai/docs/agents/overview), [Workflows overview](https://mastra.ai/docs/workflows/overview), [RAG overview](https://mastra.ai/docs/rag/overview), [Voice docs](https://mastra.ai/en/docs/voice/speech-to-text), [Evals overview](https://mastra.ai/docs/evals/overview), [Observability](https://mastra.ai/observability)

## Highest-value taxonomy additions

If the goal is to make the site reflect where the docs are today, these are the highest-value new categories to add next:

1. `Workflows / orchestration`
2. `Human-in-the-loop / approvals / interrupts`
3. `Guardrails / processors / middleware`
4. `Hosted tools / MCP / provider-native search and files`
5. `Realtime / voice / multimodal interaction`
6. `Evals / tracing / observability`

Those six areas account for most of the gap between the repo's current 22-scenario taxonomy and the latest official docs across all seven tracks.

MCP note for future coverage:

- Keep the current `8-mcp` row as the local `stdio` baseline. It is the clearest cross-framework introduction to MCP and the most comparable transport for the current matrix.
- Add a separate future scenario for `remote / hosted MCP` rather than overloading the current row. That future row should cover provider-native remote connectors (especially OpenAI and Anthropic), public URLs/tunneling, auth, and the fact that hosted MCP is a different operational model than local subprocess MCP.
