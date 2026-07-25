"""
core/memory.py — Conversation history formatter.

Converts the internal list of {"role": "user"|"assistant", "content": str}
dicts into a readable transcript string for inclusion in AI prompts.
"""


def format_history(conversation_history: list[dict]) -> str:
    """Format a conversation history list into a readable transcript string.

    Args:
        conversation_history: List of dicts with keys "role" and "content".
            role must be "user" (the student explaining) or "assistant"
            (the confused peer AI).

    Returns:
        A multi-line string suitable for embedding in a prompt, e.g.:

            Student (Explainer): Plants use sunlight to make food.
            Confused Peer (You): Wait, but where exactly does the food part come from?
            Student (Explainer): They absorb carbon dioxide and water...
    """
    lines = []
    for message in conversation_history:
        role = message.get("role", "user")
        content = message.get("content", "").strip()

        if role == "user":
            label = "Student (Explainer)"
        else:
            label = "Confused Peer (You)"

        lines.append(f"{label}: {content}")

    return "\n".join(lines)


def format_history_for_display(conversation_history: list[dict]) -> list[dict]:
    """Return the conversation history in a format ready for st.chat_message().

    Each item has: role ("user" or "assistant"), content (str).
    This is essentially a pass-through, kept as a separate function to make
    the UI code cleaner and to allow future transformation if needed.
    """
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation_history
    ]
