from backend.app.processing.text_cleaner import clean_text


messy_text = """
Artificial   Intelligence


Machine    Learning



Deep Learning
"""

cleaned_text = clean_text(messy_text)

print("--- Cleaned Text ---")
print(cleaned_text)