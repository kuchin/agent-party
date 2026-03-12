export interface Scenario {
  slug: string;
  title: string;
}

export interface Category {
  slug: string;
  contentSlug: string;
  title: string;
  scenarios: Scenario[];
}

export const categories: Category[] = [
  {
    slug: "basics",
    contentSlug: "0-basics",
    title: "Basics",
    scenarios: [
      { slug: "1-setup", title: "Setup" },
      { slug: "2-hello-world", title: "Hello World" },
      { slug: "3-instructions", title: "Instructions" },
      { slug: "4-message-history", title: "Message History" },
    ],
  },
  {
    slug: "tools",
    contentSlug: "1-tools",
    title: "Tools",
    scenarios: [
      { slug: "1-tool", title: "Tool Call" },
      { slug: "2-multi-step", title: "Multi-step" },
      { slug: "3-complex-params", title: "Complex Parameters" },
      { slug: "4-tool-error-handling", title: "Tool Error Handling" },
    ],
  },
  {
    slug: "output",
    contentSlug: "2-output",
    title: "Output",
    scenarios: [
      { slug: "1-structured-output", title: "Structured Output" },
      { slug: "2-tool-as-output", title: "Tool as Output" },
    ],
  },
  {
    slug: "streaming",
    contentSlug: "3-streaming",
    title: "Streaming",
    scenarios: [
      { slug: "1-text-streaming", title: "Text Streaming" },
      { slug: "2-stream-events", title: "Stream Events" },
    ],
  },
  {
    slug: "context",
    contentSlug: "4-context",
    title: "Context",
    scenarios: [
      { slug: "1-runtime-context", title: "Runtime Context" },
      { slug: "2-dynamic-instructions", title: "Dynamic Instructions" },
      { slug: "3-prompt-caching", title: "Prompt Caching" },
    ],
  },
  {
    slug: "memory",
    contentSlug: "5-memory",
    title: "Memory",
    scenarios: [
      { slug: "1-memory", title: "Memory" },
      { slug: "2-history-compaction", title: "History Compaction" },
    ],
  },
  {
    slug: "rag",
    contentSlug: "6-rag",
    title: "RAG",
    scenarios: [
      { slug: "1-setup", title: "Setup" },
      { slug: "2-similarity-search", title: "Similarity Search" },
      { slug: "3-keyword-search", title: "Keyword Search" },
      { slug: "4-agentic-rag", title: "Agentic RAG" },
    ],
  },
  {
    slug: "agents",
    contentSlug: "7-agents",
    title: "Agents",
    scenarios: [
      { slug: "1-subagents", title: "Subagents" },
      { slug: "2-graph", title: "Graph" },
    ],
  },
  {
    slug: "mcp",
    contentSlug: "8-mcp",
    title: "MCP",
    scenarios: [
      { slug: "1-mcp", title: "MCP" },
    ],
  },
];

export function categoryUrl(slug: string): string {
  return slug === categories[0].slug ? "/" : `/${slug}`;
}
