# llm.py
from transformers import pipeline

# Load model once
corrector = pipeline("text2text-generation", model="pszemraj/flan-t5-large-grammar-synthesis")

def correct_text(text):
    """
    Returns the full corrected paragraph (no interaction).
    """
    cleaned_text = text.strip().replace('\n', ' ')
    output = corrector(cleaned_text, max_length=512)
    return output[0]['generated_text']


