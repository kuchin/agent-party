import { generateText, type ModelMessage } from "ai";
import { openai } from "@ai-sdk/openai";

const LLM_MODEL = "gpt-5.4";

// turn 1
const messages: ModelMessage[] = [
  { role: "user", content: "What is the capital of France?" },
];
const result1 = await generateText({ model: openai(LLM_MODEL), messages });
console.log(result1.text);
// "The capital of France is Paris."

// without history, the model can't resolve "its"
const noContext = await generateText({
  model: openai(LLM_MODEL),
  prompt: "What is its population?",
});
console.log(noContext.text);
// "Could you clarify what 'its' refers to?"

// the API is stateless — pass the full conversation each call
messages.push({ role: "assistant", content: result1.text });
messages.push({ role: "user", content: "What is its population?" });

const result2 = await generateText({ model: openai(LLM_MODEL), messages });
console.log(result2.text);
// "The population of Paris is approximately 2.1 million..."
