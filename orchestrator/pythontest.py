from deep_translator import GoogleTranslator

translated = GoogleTranslator(source='english', target='bengali').translate("Good morning!")
print(translated)  # Output: শুভ সকাল!

