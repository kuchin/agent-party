import json
from openai import OpenAI
from pydantic import BaseModel

LLM_MODEL = "gpt-5.4"
FAST_MODEL = "gpt-5-mini"

client = OpenAI()

# --- Mock data ---

# past support tickets — in production this would be a database or search index
TICKETS = [
    "TK-301: Double charge on Pro plan — Refunded (2025-02-15)",
    "TK-287: Charged twice for March — Refunded (2025-03-01)",
    "TK-305: Cannot access API — Fixed API key (2025-03-03)",
]

# customer invoices — in production this would query Stripe, billing DB, etc.
INVOICES = [
    "INV-440: $49 on 2025-03-01 (paid)",
    "INV-441: $49 on 2025-03-01 (paid — duplicate)",
]

# --- Child tool implementations ---

def search_tickets(query: str) -> str:
    """Search past support tickets by keyword."""
    print(f"-> call: search_tickets({query!r})")
    # split into words so partial matches work — the LLM might send
    # "customers charged twice" but individual words like "charge" still match
    words = query.lower().split()
    matches = [t for t in TICKETS if any(w in t.lower() for w in words)]
    result = "\n".join(matches) if matches else "No similar tickets found."
    print(f"-> result: {len(matches)} tickets found")
    return result

def lookup_invoices() -> str:
    """Look up the current customer's recent invoices."""
    print("-> call: lookup_invoices()")
    result = "\n".join(INVOICES)
    print(f"-> result: {len(INVOICES)} invoices")
    return result

# --- Subagent helper ---
# A subagent is just an LLM call with its own instructions, tools, and
# message history. This helper encapsulates the ReAct loop so each
# specialist can run independently — the parent gets back a string.

def run_subagent(model, instructions, tools, registry, prompt):
    input = [
        {"role": "developer", "content": instructions},
        {"role": "user", "content": prompt},
    ]
    while True:
        response = client.responses.create(model=model, input=input, tools=tools)
        tool_calls = [i for i in response.output if i.type == "function_call"]
        if not tool_calls:
            return response.output_text
        input += response.output
        for tc in tool_calls:
            result = registry[tc.name](**json.loads(tc.arguments))
            input.append({
                "type": "function_call_output",
                "call_id": tc.call_id,
                "output": result,
            })

# --- Tool schemas for specialists ---

class SearchTicketsParams(BaseModel):
    query: str

class LookupInvoicesParams(BaseModel):
    pass

# ticket search specializes in RETRIEVAL — finding patterns in past data.
# uses a faster/cheaper model because the task is lookup, not reasoning.
ticket_tools = [{
    "type": "function",
    "name": "search_tickets",
    "description": "Search past support tickets by keyword",
    "parameters": SearchTicketsParams.model_json_schema(),
}]
ticket_registry = {"search_tickets": search_tickets}
ticket_instructions = """\
You search past support tickets and summarize what you find.
Report how many similar issues exist and how they were resolved.
"""

# billing specializes in POLICY — applying business rules to specific situations.
# uses the main model because refund decisions require judgment.
billing_tools = [{
    "type": "function",
    "name": "lookup_invoices",
    "description": "Look up the current customer's recent invoices",
    "parameters": LookupInvoicesParams.model_json_schema(),
}]
billing_registry = {"lookup_invoices": lookup_invoices}
billing_instructions = """\
You are a billing specialist. Look up invoices and apply refund policy.
Refund policy: duplicate charges are always refundable.
"""

# --- Parent tools (each wraps a subagent) ---
# The parent has no domain tools — it only delegates to specialists.
# This keeps each specialist's context focused: the ticket searcher never sees
# invoice data, and the billing agent never sees ticket history.
# Without this separation, irrelevant context from one domain can confuse
# reasoning in another (sometimes called "context poisoning").
# See flow.txt for the delegation diagram this code implements.

def search_previous_tickets(query: str) -> str:
    """Search past tickets for similar issues."""
    print(f"-> call: search_previous_tickets({query!r})")
    return run_subagent(
        FAST_MODEL, ticket_instructions, ticket_tools, ticket_registry, query,
    )

def check_billing(question: str) -> str:
    """Ask the billing specialist about charges, invoices, or refunds."""
    print(f"-> call: check_billing({question!r})")
    return run_subagent(
        LLM_MODEL, billing_instructions, billing_tools, billing_registry, question,
    )

# --- Parent agent tool schemas and registry ---

class SearchPreviousTicketsParams(BaseModel):
    query: str

class CheckBillingParams(BaseModel):
    question: str

parent_registry = {
    "search_previous_tickets": search_previous_tickets,
    "check_billing": check_billing,
}

parent_tools = [
    {
        "type": "function",
        "name": "search_previous_tickets",
        "description": "Search past tickets for similar issues",
        "parameters": SearchPreviousTicketsParams.model_json_schema(),
    },
    {
        "type": "function",
        "name": "check_billing",
        "description": "Ask the billing specialist about charges, invoices, or refunds",
        "parameters": CheckBillingParams.model_json_schema(),
    },
]

# --- Parent agent loop ---

parent_instructions = """\
You are a customer support agent. Use your specialists:
search_previous_tickets checks for similar past issues,
check_billing handles billing or refund questions.
Combine their findings into a single helpful response.
"""

user_prompt = """\
I was charged twice this month.
Has this happened to other customers? Can I get a refund?
"""

input = [
    {
        "role": "developer",
        "content": parent_instructions,
    },
    {
        "role": "user",
        "content": user_prompt,
    },
]

while True:
    response = client.responses.create(
        model=LLM_MODEL, input=input, tools=parent_tools,
    )
    tool_calls = [i for i in response.output if i.type == "function_call"]
    if not tool_calls:
        break
    input += response.output
    for tc in tool_calls:
        result = parent_registry[tc.name](**json.loads(tc.arguments))
        input.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result,
        })

print(response.output_text)
# -> call: search_previous_tickets('double charge')
#   -> call: search_tickets('double charge')
#   -> result: 2 tickets found
# -> call: check_billing('charged twice, eligible for refund?')
#   -> call: lookup_invoices()
#   -> result: 2 invoices
# "We've seen similar double-charge reports — both resolved with refunds.
#  You have two $49 charges from March 1st. Duplicate charges are always
#  refundable — I'll process your refund right away."
