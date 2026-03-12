import { defineCollection, z } from "astro:content";
import fs from "node:fs";
import path from "node:path";
import { createHighlighter } from "shiki";

const shikiLang: Record<string, string> = {
  ts: "typescript",
  py: "python",
  prisma: "prisma",
  sh: "bash",
  txt: "text",
};

const filenameLang: Record<string, string> = {
  ".env": "dotenv",
};

function fileLang(file: string): { ext: string; lang: string } {
  if (filenameLang[file]) return { ext: file, lang: filenameLang[file] };
  const ext = path.extname(file).slice(1);
  return { ext, lang: shikiLang[ext] || ext };
}

// Keep `agent.py` ahead of `agent_async.py` without forcing numeric prefixes
// in the simple single-file snippet folders.
function compareSnippetFiles(a: string, b: string): number {
  if (a.startsWith(".")) return 1;
  if (b.startsWith(".")) return -1;

  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    if (a[i] === b[i]) continue;
    if (a[i] === "." && b[i] === "_") return -1;
    if (a[i] === "_" && b[i] === ".") return 1;
    return a.localeCompare(b);
  }

  return a.length - b.length;
}

const snippetLoader = {
  name: "snippet-loader",
  async load({ store, logger }: { store: any; logger: any }) {
    const contentDir = path.resolve("./content");

    if (!fs.existsSync(contentDir)) {
      logger.warn("No content directory found");
      return;
    }

    const dirs = (dir: string) =>
      fs
        .readdirSync(dir, { withFileTypes: true })
        .filter((d) => d.isDirectory())
        .sort((a, b) => a.name.localeCompare(b.name));

    // Collect unique languages
    const langs = new Set<string>();
    for (const cat of dirs(contentDir)) {
      for (const scenario of dirs(path.join(contentDir, cat.name))) {
        for (const framework of dirs(path.join(contentDir, cat.name, scenario.name))) {
          const frameworkPath = path.join(contentDir, cat.name, scenario.name, framework.name);
          for (const file of fs.readdirSync(frameworkPath).filter((f) => !f.startsWith(".") || f === ".env")) {
            langs.add(fileLang(file).lang);
          }
        }
      }
    }

    const highlighter = await createHighlighter({
      themes: ["github-dark", "github-light"],
      langs: [...langs],
    });

    for (const cat of dirs(contentDir)) {
      for (const scenario of dirs(path.join(contentDir, cat.name))) {
        for (const framework of dirs(path.join(contentDir, cat.name, scenario.name))) {
          const frameworkPath = path.join(contentDir, cat.name, scenario.name, framework.name);
          const files = fs.readdirSync(frameworkPath)
            .filter((f) => !f.startsWith(".") || f === ".env")
            .sort(compareSnippetFiles);

          const snippetFiles = files.map((file) => {
            const { ext, lang } = fileLang(file);
            const code = fs.readFileSync(path.join(frameworkPath, file), "utf-8");
            const html = highlighter.codeToHtml(code.trim(), {
              lang,
              themes: {
                dark: "github-dark",
                light: "github-light",
              },
              defaultColor: "dark",
            });
            return { filename: file, language: ext, code, html };
          });

          store.set({
            id: `${cat.name}/${scenario.name}/${framework.name}`,
            data: {
              categorySlug: cat.name,
              scenarioSlug: scenario.name,
              frameworkId: framework.name,
              files: snippetFiles,
            },
          });
        }
      }
    }

    highlighter.dispose();
    logger.info(`Loaded ${store.keys().length} snippets`);
  },
};

const snippets = defineCollection({
  loader: snippetLoader,
  schema: z.object({
    categorySlug: z.string(),
    scenarioSlug: z.string(),
    frameworkId: z.string(),
    files: z.array(
      z.object({
        filename: z.string(),
        language: z.string(),
        code: z.string(),
        html: z.string(),
      }),
    ),
  }),
});

export const collections = { snippets };
