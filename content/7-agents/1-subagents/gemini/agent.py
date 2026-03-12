from google import genai
from google.genai import types

LLM_MODEL = "gemini-pro-latest"
FAST_MODEL = "gemini-flash-latest"

client = genai.Client()

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

# --- Child tools (used by specialists, not by the parent) ---

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
# Gemini's automatic function calling runs the full tool loop internally,
# so a subagent is just a generate_content call with its own model,
# instructions, and tools. The parent gets back a string.

def run_subagent(model, instructions, tools, prompt):
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=instructions,
    )
    response = client.models.generate_content(
        model=model, config=config, contents=prompt,
    )
    return response.text

# --- Parent tools (each wraps a subagent) ---
# The parent has no domain tools — it only delegates to specialists.
# This keeps each specialist's context focused: the ticket searcher never sees
# invoice data, and the billing agent never sees ticket history.
# Without this separation, irrelevant context from one domain can confuse
# reasoning in another (sometimes called "context poisoning").
# See flow.txt for the delegation diagram this code implements.

# Ticket search specializes in RETRIEVAL — finding patterns in past data.
# Uses a faster/cheaper model because the task is lookup, not reasoning.
ticket_instructions = """\
You search past support tickets and summarize what you find.
Report how many similar issues exist and how they were resolved.
"""

def search_previous_tickets(query: str) -> str:
    """Search past tickets for similar issues."""
    print(f"-> call: search_previous_tickets({query!r})")
    return run_subagent(FAST_MODEL, ticket_instructions, [search_tickets], query)

# Billing specializes in POLICY — applying business rules to specific situations.
# Uses the main model because refund decisions require judgment.
billing_instructions = """\
You are a billing specialist. Look up invoices and apply refund policy.
Refund policy: duplicate charges are always refundable.
"""

def check_billing(question: str) -> str:
    """Ask the billing specialist about charges, invoices, or refunds."""
    print(f"-> call: check_billing({question!r})")
    return run_subagent(LLM_MODEL, billing_instructions, [lookup_invoices], question)

# --- Parent agent ---
# automatic function calling: SDK runs the ReAct loop for the parent too

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

config = types.GenerateContentConfig(
    tools=[search_previous_tickets, check_billing],
    system_instruction=parent_instructions,
)

response = client.models.generate_content(
    model=LLM_MODEL,
    config=config,
    contents=user_prompt,
)
print(response.text)
# -> call: search_previous_tickets('double charge')
#   -> call: search_tickets('double charge')
#   -> result: 2 tickets found
# -> call: check_billing('charged twice, eligible for refund?')
#   -> call: lookup_invoices()
#   -> result: 2 invoices
# "We've seen similar double-charge reports — both resolved with refunds.
#  You have two $49 charges from March 1st. Duplicate charges are always
#  refundable — I'll process your refund right away."
