from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

LLM_MODEL = "gpt-5.4"
FAST_MODEL = "gpt-5-mini"

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

@tool
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

@tool
def lookup_invoices() -> str:
    """Look up the current customer's recent invoices."""
    print("-> call: lookup_invoices()")
    result = "\n".join(INVOICES)
    print(f"-> result: {len(INVOICES)} invoices")
    return result

# --- Specialist agents ---
# Each specialist gets its own model, tools, and instructions.
# The ticket searcher specializes in RETRIEVAL — finding patterns in past data.
# Uses a faster/cheaper model because the task is lookup, not reasoning.
ticket_model = ChatOpenAI(model=FAST_MODEL)
ticket_agent = create_agent(ticket_model, [search_tickets])

# The billing specialist applies POLICY — business rules to specific situations.
# Uses the main model because refund decisions require judgment.
billing_model = ChatOpenAI(model=LLM_MODEL)
billing_agent = create_agent(billing_model, [lookup_invoices])

# --- Parent tools (each wraps a subagent) ---
# The parent has no domain tools — it only delegates to specialists.
# This keeps each specialist's context focused: the ticket searcher never sees
# invoice data, and the billing agent never sees ticket history.
# Without this separation, irrelevant context from one domain can confuse
# reasoning in another (sometimes called "context poisoning").
# See flow.txt for the delegation diagram this code implements.

@tool
def search_previous_tickets(query: str) -> str:
    """Search past tickets for similar issues."""
    print(f"-> call: search_previous_tickets({query!r})")
    # this tool wraps a subagent — the parent sees only the final answer
    result = ticket_agent.invoke({
        "messages": [
            SystemMessage(content="""\
You search past support tickets and summarize what you find.
Report how many similar issues exist and how they were resolved.
"""),
            ("user", query),
        ]
    })
    return result["messages"][-1].content

@tool
def check_billing(question: str) -> str:
    """Ask the billing specialist about charges, invoices, or refunds."""
    print(f"-> call: check_billing({question!r})")
    result = billing_agent.invoke({
        "messages": [
            SystemMessage(content="""\
You are a billing specialist. Look up invoices and apply refund policy.
Refund policy: duplicate charges are always refundable.
"""),
            ("user", question),
        ]
    })
    return result["messages"][-1].content

# --- Parent agent ---

parent_model = ChatOpenAI(model=LLM_MODEL)
agent = create_agent(parent_model, [search_previous_tickets, check_billing])
result = agent.invoke({
    "messages": [("user", """\
I was charged twice this month.
Has this happened to other customers? Can I get a refund?
""")]
})
print(result["messages"][-1].content)
# -> call: search_previous_tickets('double charge')
#   -> call: search_tickets('double charge')
#   -> result: 2 tickets found
# -> call: check_billing('charged twice, eligible for refund?')
#   -> call: lookup_invoices()
#   -> result: 2 invoices
# "We've seen similar double-charge reports — both resolved with refunds.
#  You have two $49 charges from March 1st. Duplicate charges are always
#  refundable — I'll process your refund right away."
