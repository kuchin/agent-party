from langchain.tools import tool
from langchain.messages import ToolMessage
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_openai import ChatOpenAI

LLM_MODEL = "gpt-5.4"

model = ChatOpenAI(model=LLM_MODEL)

# Mock calendar. In production this would query Google Calendar, Outlook, etc.
CALENDAR = {
    "09:00": "Team standup",
    "14:00": "Design review",
    "16:00": "1:1 with manager",
}


@tool
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

# wrap_tool_call catches errors and surfaces them to the LLM
@wrap_tool_call
def handle_errors(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Error: {e}",
            tool_call_id=request.tool_call["id"],
        )

agent = create_agent(
    model,
    [schedule_meeting],
    system_prompt="""\
You schedule meetings with the schedule_meeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
""",
    middleware=[handle_errors],
)
result = agent.invoke({
    "messages": [("user", "Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.")]
})
print(result["messages"][-1].content)
# -> call: schedule_meeting(time='14:00', title='Discuss Q3 roadmap with Sarah')
# -> error: 14:00 is already booked (Design review)
# -> call: schedule_meeting(time='15:00', title='Discuss Q3 roadmap with Sarah')
# -> result: Scheduled 'Discuss Q3 roadmap with Sarah' at 15:00.
# "Scheduled with Sarah for 15:00: Discuss Q3 roadmap."
