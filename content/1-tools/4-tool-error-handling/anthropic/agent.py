import anthropic

LLM_MODEL = "claude-opus-4-6"

client = anthropic.Anthropic()

# Mock calendar. In production this would query Google Calendar, Outlook, etc.
CALENDAR = {
    "09:00": "Team standup",
    "14:00": "Design review",
    "16:00": "1:1 with manager",
}


def schedule_meeting(time: str, title: str) -> str:
    """Schedule a meeting at a given time."""
    print(f"-> call: schedule_meeting(time={time!r}, title={title!r})")
    if time in CALENDAR:
        # Times are zero-padded HH:MM strings, so plain string comparison
        # keeps them in chronological order for this example.
        available = [
            slot
            for slot in [f"{hour:02d}:00" for hour in range(9, 18)]
            if slot not in CALENDAR and slot > time
        ]
        print(f"-> error: {time} is already booked ({CALENDAR[time]})")
        raise ValueError(
            f"{time} is already booked ({CALENDAR[time]}). "
            f"Next available slots after {time}: {', '.join(available)}"
        )
    result = f"Scheduled '{title}' at {time}."
    CALENDAR[time] = title
    print(f"-> result: {result}")
    return result

tools = [{
    "name": "schedule_meeting",
    "description": "Schedule a meeting at a given time.",
    "input_schema": {
        "type": "object",
        "properties": {
            "time": {"type": "string"},
            "title": {"type": "string"},
        },
        "required": ["time", "title"],
    },
}]

messages = [{
    "role": "user",
    "content": "Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.",
}]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=1024,
        system="""\
You schedule meetings with the schedule_meeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
""",
        tools=tools,
        messages=messages,
    )
    if response.stop_reason != "tool_use":
        break
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            try:
                result = schedule_meeting(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
            except Exception as e:
                # is_error tells the LLM this tool call failed and should be repaired
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(e),
                    "is_error": True,
                })
    messages.append({"role": "user", "content": tool_results})

print(response.content[0].text)
# -> call: schedule_meeting(time='14:00', title='Meeting with Sarah - Discuss Q3 Roadmap')
# -> error: 14:00 is already booked (Design review)
# -> call: schedule_meeting(time='15:00', title='Meeting with Sarah - Discuss Q3 Roadmap')
# -> result: Scheduled 'Meeting with Sarah - Discuss Q3 Roadmap' at 15:00.
# "Your meeting has been scheduled! Here's a summary:
# - Title: Meeting with Sarah - Discuss Q3 Roadmap
# - Time: 15:00 (moved from 14:00, which was occupied by a Design Review)
# Let me know if you'd like to adjust anything!"
