from services.review_manager import review_llm_corrections

original = "He go to the market and buy apple."
corrected = "He went to the market and bought an apple."

result = review_llm_corrections(None, original, corrected)

print("\n[Original]")
print(result["original"])
print("\n[Corrected]")
print(result["corrected"])
print("\n[Diffs]")
for change in result["diffs"]:
    print(f"- {change['tag'].upper()}: '{change['from']}' → '{change['to']}' "
          f"(words {change['original_start']}–{change['original_end']})")
