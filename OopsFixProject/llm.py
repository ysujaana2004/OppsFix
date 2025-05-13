# llm.py
from transformers import pipeline

# Load model once
# corrector = pipeline("text2text-generation", model="pszemraj/flan-t5-large-grammar-synthesis")
corrector = pipeline("text2text-generation", model="vennify/t5-base-grammar-correction")

def correct_text(text):
    """
    Returns the full corrected paragraph (no interaction).
    """
    # cleaned_text = text.strip().replace('\n', ' ')
    prompt = f"grammar: {text}"
    output = corrector(prompt, max_length=512)
    return output[0]['generated_text']


