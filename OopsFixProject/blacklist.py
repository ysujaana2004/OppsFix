# blacklist.py

# Simulated in-memory blacklist
BLACKLISTED_WORDS = {"dumb", "stupid", "idiot", "ugly"}

def filter_blacklisted_words(text):
    """
    Replaces blacklisted words with asterisks.
    Returns the filtered text and the total token cost (based on length of blacklisted words).
    """
    words = text.split()
    cost = 0
    filtered_words = []

    for word in words:
        clean_word = word.lower().strip('.,!?')  # basic cleanup
        if clean_word in BLACKLISTED_WORDS:
            masked = '*' * len(word)
            filtered_words.append(masked)
            cost += len(word)
        else:
            filtered_words.append(word)

    filtered_text = ' '.join(filtered_words)
    return filtered_text, cost

def suggest_blacklist_word(user, word):
    """
    Paid/Free user suggests a new word to be blacklisted.
    Super user must approve it later.
    """
    if hasattr(user, 'blacklist_suggestions'):
        user.blacklist_suggestions.append(word)
        print(f"'{word}' suggested for blacklist.")
    else:
        print("You don't have permission to suggest blacklist words.")

if __name__ == "__main__":
    text = "you are a dumb idiot. You are not very smart!"
    print (filter_blacklisted_words(text))
