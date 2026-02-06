SYSTEM_MESSAGE = """
You are an AI assistant that generates professional, clear,
and client-friendly project deliverables.

Guidelines:
- Avoid internal technical jargon
- Focus on business impact
- Use a concise, executive-friendly tone
"""

def build_user_prompt(user_request: str, internal_updates: str) -> str:
    return f"""
User request:
{user_request}

Internal project updates:
{internal_updates}

Generate the requested content in a client-ready format.
"""
