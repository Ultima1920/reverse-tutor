def format_history(conversation_history):
    """
    Formats the conversation history list into a string for the prompt.
    Expects history format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    formatted = "Conversation History:\n"
    if not conversation_history:
        return formatted + "(No history yet. Start the conversation.)\n"
        
    for msg in conversation_history:
        role = "Student (Explainer)" if msg["role"] == "user" else "Confused Peer (You)"
        formatted += f"{role}: {msg['content']}\n\n"
    return formatted
