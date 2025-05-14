# services/llm_handler.py

from transformers import pipeline
from difflib import SequenceMatcher

class LLMHandler:
    def __init__(self, whitelist=None):
        # Load grammar correction model
        self.model = pipeline("text2text-generation", model="pszemraj/flan-t5-large-grammar-synthesis")
        self.whitelist = set(whitelist) if whitelist else set()

    def correct_text(self, text):
        prompt = text.strip().replace('\n', ' ')
        output = self.model(prompt, max_length=512)[0]['generated_text']
        return output

    def compare_texts(self, original, corrected):
        """
        Returns a list of (original_word, corrected_word, changed_bool).
        """
        orig_words = original.strip().split()
        corr_words = corrected.strip().split()

        matcher = SequenceMatcher(None, orig_words, corr_words)
        result = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    result.append((orig_words[i], corr_words[i - i1 + j1], False))
            elif tag in ['replace', 'delete', 'insert']:
                for i in range(i1, i2):
                    orig = orig_words[i]
                    corr = corr_words[j1 + (i - i1)] if j1 + (i - i1) < len(corr_words) else ''
                    result.append((orig, corr, True))

        return result

    def is_whitelisted(self, word):
        return word.lower() in self.whitelist

    def add_to_whitelist(self, word):
        self.whitelist.add(word.lower())
