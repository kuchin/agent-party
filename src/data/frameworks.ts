export interface FrameworkDef {
  id: string;
  name: string;
  language: "typescript" | "python";
  fileExtension: string;
  website: string;
  color: string;
  logoPath: string;
  logoStyle?: string;
}

export const frameworks: FrameworkDef[] = [
  {
    id: "openai",
    name: "OpenAI",
    language: "python",
    fileExtension: "py",
    website: "https://platform.openai.com/docs/",
    color: "#E0E0E0",
    logoPath: "/framework/openai.svg",
    logoStyle: "filter: brightness(0) invert(0.94);",
  },
  {
    id: "anthropic",
    name: "Anthropic",
    language: "python",
    fileExtension: "py",
    website: "https://docs.anthropic.com/",
    color: "#D4A27F",
    logoPath: "/framework/anthropic.svg",
  },
  {
    id: "gemini",
    name: "Gemini",
    language: "python",
    fileExtension: "py",
    website: "https://ai.google.dev/gemini-api/docs",
    color: "#4285F4",
    logoPath: "/framework/gemini.svg",
  },
  {
    id: "pydantic",
    name: "Pydantic AI",
    language: "python",
    fileExtension: "py",
    website: "https://ai.pydantic.dev/",
    color: "#E520E9",
    logoPath: "/framework/pydantic.svg",
  },
  {
    id: "langgraph",
    name: "LangGraph",
    language: "python",
    fileExtension: "py",
    website: "https://langchain-ai.github.io/langgraph/",
    color: "#1C3C3C",
    logoPath: "/framework/langgraph.png",
    logoStyle: "filter: brightness(0) invert(0.94);",
  },
  {
    id: "aisdk",
    name: "AI SDK",
    language: "typescript",
    fileExtension: "ts",
    website: "https://ai-sdk.dev/",
    color: "#030303",
    logoPath: "/framework/aisdk.svg",
    logoStyle: "filter: brightness(0) invert(0.94);",
  },
  {
    id: "mastra",
    name: "Mastra",
    language: "typescript",
    fileExtension: "ts",
    website: "https://mastra.ai/",
    color: "#5856D6",
    logoPath: "/framework/mastra.svg",
  },
];

export const frameworkMap = Object.fromEntries(
  frameworks.map((f) => [f.id, f]),
);
