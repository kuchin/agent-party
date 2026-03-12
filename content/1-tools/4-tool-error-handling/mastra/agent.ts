import { Agent } from "@mastra/core/agent";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

// model specified as "provider/model-name" string
const LLM_MODEL = "openai/gpt-5.4";

const CALENDAR = {
  "09:00": "Team standup",
  "14:00": "Design review",
  "16:00": "1:1 with manager",
};

const scheduleMeeting = createTool({
  id: "schedule-meeting",
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
      // Returning the error text keeps the retry behavior without noisy logs.
      console.log(`-> error: ${time} is already booked (${CALENDAR[time as keyof typeof CALENDAR]})`);
      return `Error: ${time} is already booked (${CALENDAR[time as keyof typeof CALENDAR]}). `
        + `Next available slots after ${time}: ${available.join(", ")}`;
    }
    const result = `Scheduled '${title}' at ${time}.`;
    CALENDAR[time as keyof typeof CALENDAR] = title;
    console.log(`-> result: ${result}`);
    return result;
  },
});

const agent = new Agent({
  name: "error-handling-agent",
  instructions: `\
You schedule meetings with the scheduleMeeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
`,
  model: LLM_MODEL,
  tools: { scheduleMeeting },
});

const result = await agent.generate("Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.");
console.log(result.text);
// -> call: scheduleMeeting(time="14:00", title="Meeting with Sarah: discuss Q3 roadmap")
// -> error: 14:00 is already booked (Design review)
// -> call: scheduleMeeting(time="15:00", title="Meeting with Sarah: discuss Q3 roadmap")
// -> result: Scheduled 'Meeting with Sarah: discuss Q3 roadmap' at 15:00.
// "Scheduled with Sarah at 15:00 to discuss Q3 roadmap."
