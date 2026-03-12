import json
from openai import OpenAI
from pydantic import BaseModel


LLM_MODEL = "gpt-5.4"
client = OpenAI()

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


class ScheduleMeetingParams(BaseModel):
    time: str
    title: str

# build tool schema and register for dispatch
registry = {}

def to_tool(fn, params):
    registry[fn.__name__] = fn
    return {
        "type": "function",
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": params.model_json_schema(),
    }

tools = [to_tool(schedule_meeting, ScheduleMeetingParams)]

conversation = [{
    "role": "user",
    "content": "Schedule a meeting with Sarah at 14:00 to discuss Q3 roadmap.",
}]

# ReAct loop: LLM calls tools until it can answer
while True:
    response = client.responses.create(
        model=LLM_MODEL,
        instructions="""\
You schedule meetings with the schedule_meeting tool.
If a slot is unavailable, pick the next available slot
automatically and retry.
""",
        input=conversation,
        tools=tools,
    )
    tool_calls = [i for i in response.output if i.type == "function_call"]
    if not tool_calls:
        break
    conversation += response.output
    for tc in tool_calls:
        try:
            result = registry[tc.name](**json.loads(tc.arguments))
        except Exception as e:
            # send the error back so the LLM can repair the tool call
            result = f"Error: {e}"
        conversation.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result,
        })

print(response.output_text)
# -> call: schedule_meeting(time='14:00', title='Meeting with Sarah: discuss Q3 roadmap')
# -> error: 14:00 is already booked (Design review)
# -> call: schedule_meeting(time='15:00', title='Meeting with Sarah: discuss Q3 roadmap')
# -> result: Scheduled 'Meeting with Sarah: discuss Q3 roadmap' at 15:00.
# "Scheduled for 15:00: Meeting with Sarah to discuss Q3 roadmap."
