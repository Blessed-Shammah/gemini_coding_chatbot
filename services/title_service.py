def title_from_first_message(text: str) -> str:
    """
    Tiny heuristic to title a conversation from its first user message.
    """
    if not text:
        return "New Chat"
    t = text.strip().replace("\n", " ")
    return (t[:28] + "…") if len(t) > 29 else t
