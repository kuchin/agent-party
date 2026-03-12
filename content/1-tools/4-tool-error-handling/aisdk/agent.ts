import { ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const LLM_MODEL = "gpt-5.4";

const CALENDAR = {
  "09:00": "Team standup",
  "14:00": "Design review",
  "16:00": "1:1 with manager",
};

const scheduleMeeting = tool({
  description: "Schedule a meeting at a given time",
  inputSchema: z.object({
    time: z.string(),
    title: z.string(),
  }),
  execute: async ({ time, title }) => {
    console.log(`-> call: scheduleMeeting(time=${JSON.stringify(time)}, title=${JSON.stringify(title)})`);
    if (time in CALENDAR) {
      // Times are zero-padded HH:MM strings, so plain string comparison
      // keeps them in chronological order for this example.
      const available = Array.from({ length: 9 }, (_, index) => `${String(index + 9).padStart(2, "0")}:00`)
        .filter((slot) => !(slot in CALENDAR))
        .filter((slot) => slot > time);
      // thrown errors are surfaced back to the LLM automatically
      console.log(`-> error: ${time} is already booked (${CALENDAR[time as keyof typeof CALENDAR]})`);
      throw new Error(
        `${time} is already booked (${CALENDAR[time as keyof typeof CALENDAR]}). `
        + `Next available slots after ${time}: ${available.join(", ")}`
      );
    }
    const result = `Scheduled '${title}' at ${time}.`;
    CALENDAR[time as keyof typeof CALENDAR] = title;
    console.log(`-> result: ${result}`);
    return result;
  },
});

const agent = new ToolLoopAgent({
  model: openai(LLM_MODEL),
  instructions: `\
You schedule meetings with the scheduleMeeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
`,
  tools: { scheduleMeeting },
});

const result = await agent.generate({
  prompt: "Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.",
});
console.log(result.text);
// -> call: scheduleMeeting(time="14:00", title="Discuss Q3 roadmap with Sarah")
// -> error: 14:00 is already booked (Design review)
// -> call: scheduleMeeting(time="15:00", title="Discuss Q3 roadmap with Sarah")
// -> result: Scheduled 'Discuss Q3 roadmap with Sarah' at 15:00.
// "Scheduled with Sarah at 15:00: Discuss Q3 roadmap."
