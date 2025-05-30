from fayeemai import *

text = "Hello, how are you? I hope you are doing well."
text2 = "This is a test sentence for translation."

texts = [text, text2]

def generate_texts(prompt):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Generation Error: {e}")
        return ""

def translate_bangla(text: str) -> str:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"Translate the following English text into Bengali:\n\n{text} just return the translated text without any additional information."
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Translation Error: {e}")
        return text
    


def translate_multiple_texts_to_bangla(texts: list[str]) -> list[str]:
    prompt = "Translate the following English texts into Bengali. Return them as a numbered list:\n\n"
    for i, text in enumerate(texts):
        prompt += f"{i+1}. {text.strip()}\n"
    prompt += "\nPlease return the translations in the same order as the original texts."
    prompt += "just return the translated text without any additional information."
    
    try:
        result = generate_texts(prompt)
        lines = result.strip().split("\n")
        return [line.split(". ", 1)[1].strip() for line in lines if ". " in line]
    except Exception as e:
        print(f"Gemini batch translation error: {e}")
        return texts
    

# print(translate_multiple_texts_to_bangla(texts))

