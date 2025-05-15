def get_user_statistics(user):
    stats = {
        "Username": user.username,
        "User Type": user.user_type,
        "Tokens Remaining": user.tokens,
        "Texts Submitted": len(user.text_history),
        "LLM Corrections": sum(1 for c in user.corrections if c["method"].lower() == "llm"),
        "Self Corrections": sum(1 for c in user.corrections if c["method"].lower() == "self"),
        "Whitelisted Phrases": len(user.whitelist) if hasattr(user, "whitelist") else 0
    }
    return stats
