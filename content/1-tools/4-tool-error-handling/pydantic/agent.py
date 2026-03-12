from pydantic_ai import Agent, ModelRetry

LLM_MODEL = "openai:gpt-5.4"

# Mock calendar. In production this would query Google Calendar, Outlook, etc.
CALENDAR = {
    "09:00": "Team standup",
    "14:00": "Design review",
    "16:00": "1:1 with manager",
}

# These instructions make the model repair the tool call and retry automatically.
agent = Agent(
    LLM_MODEL,
    instructions="""\
You schedule meetings with the schedule_meeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
""",
)

@agent.tool_plain(retries=2)
def schedule_meeting(time: str, title: str) -> str:
    """Schedule a meeting at a given time.

    Args:
        time: Time in HH:MM 24-hour format, e.g. '09:00', '14:30'.
        title: Meeting title.
    """
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
        # ModelRetry sends the tool failure back so the model can fix the input.
        raise ModelRetry(
            f"{time} is already booked ({CALENDAR[time]}). "
            f"Next available slots after {time}: {', '.join(available)}"
        )

    CALENDAR[time] = title
    print(f"-> result: Scheduled '{title}' at {time}")
    return f"Scheduled '{title}' at {time}."

result = agent.run_sync("Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.")
print(result.output)
# -> call: schedule_meeting(time='14:00', title='Discuss Q3 roadmap with Sarah')
# -> error: 14:00 is already booked (Design review)
# -> call: schedule_meeting(time='15:00', title='Discuss Q3 roadmap with Sarah')
# -> result: Scheduled 'Discuss Q3 roadmap with Sarah' at 15:00
# "Scheduled with Sarah at 15:00: Discuss Q3 roadmap."
