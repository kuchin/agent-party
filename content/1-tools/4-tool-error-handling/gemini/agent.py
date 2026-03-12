from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"

client = genai.Client()

# Mock calendar. In production this would query Google Calendar, Outlook, etc.
CALENDAR = {
    "09:00": "Team standup",
    "14:00": "Design review",
    "16:00": "1:1 with manager",
}


# with automatic calling, return error info instead of raising —
# the SDK sends it back and the model can retry with a better call
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
        return (
            f"Error: {time} is already booked ({CALENDAR[time]}). "
            f"Next available slots after {time}: {', '.join(available)}"
        )
    result = f"Scheduled '{title}' at {time}."
    CALENDAR[time] = title
    print(f"-> result: {result}")
    return result

config = types.GenerateContentConfig(
    tools=[schedule_meeting],
    system_instruction="""\
You schedule meetings with the schedule_meeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
""",
)

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents="Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.",
)
print(response.text)
# -> call: schedule_meeting(time='14:00', title='Discuss Q3 roadmap with Sarah')
# -> error: 14:00 is already booked (Design review)
# -> call: schedule_meeting(time='15:00', title='Discuss Q3 roadmap with Sarah')
# -> result: Scheduled 'Discuss Q3 roadmap with Sarah' at 15:00.
# "The 14:00 slot was already booked, so I automatically scheduled the
# meeting with Sarah to discuss the Q3 roadmap for the next available
# slot at 15:00."
