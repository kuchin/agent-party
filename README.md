# Agent Party

Side-by-side comparison of AI agent framework syntax. See how the same agent pattern looks across different SDKs and frameworks.

Inspired by [component-party.dev](https://component-party.dev).

## Frameworks

**Python:** OpenAI SDK, Anthropic SDK, Gemini SDK, Pydantic AI, LangGraph

**TypeScript:** Mastra, AI SDK

## Categories

| Category | Scenarios |
| :--- | :--- |
| The Basics | Setup, Hello World, Instructions |
| Tools | Tool Call, Multi-step, Complex Parameters, Tool Error Handling |
| Output | Structured Output, Tool as Output |
| Streaming | Text Streaming, Stream Events |

## Tech Stack

- [Astro](https://astro.build) (static site generation)
- [Tailwind CSS v4](https://tailwindcss.com)
- [Shiki](https://shiki.style) (syntax highlighting)

## Development

```sh
bun install
bun dev
```

## Build

```sh
bun run build
```

## Project Structure

```
content/              # Agent code snippets organized by category/scenario/framework
src/
  components/         # Astro components (CategoryPage, FrameworkSelector, etc.)
  data/               # Framework and category definitions
  layouts/            # Page layout
  pages/              # Routes (index, about, each category)
```

## Contributing

To add a new framework, create a directory for it under each scenario in `content/` and register it in `src/data/frameworks.ts`.

## Author

Built by [Dima Kuchin](https://github.com/kuchin) at [Mirable](https://mirable.io).
