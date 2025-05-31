from .fayeemai import *
import base64
import json
# from deep_translator import GoogleTranslator

def generate_texts(prompt):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Generation Error: {e}")
        return ""

def translate_bangla_single(text: str) -> str:
    try:
        prompt = f"Translate the following English text into Bengali:\n\n{text} just return the translated text without any additional information."
        response = generate_texts(prompt)
        return response
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
    
    


def extract_text_from_pdf(file_list):
    # Use PyMuPDF, pdfminer, or PyPDF2
    text = ""
    for pdf_file in file_list:
        text += pdf_file.read().decode('utf-8')  # or proper PDF parse
    return text

class Course:
    def __init__(self, title, subject, description):
        self.title = title
        self.subject = subject
        self.description = description

        


    def to_dict(self):
        return {
            "title": self.title,
            "subject": self.subject,
            "description": self.description
        }


def create_course(user_id, course_title, course_subject, course_description):

    # This function should call the backend to create a course
    # For example:
    # return requests.post(f"{BACKEND1_BASE_URL}/create_course", json={
    #     "user_id": user_id,
    #     "course_title": course_title,
    #     "text": text
    # }).json()
    pass



# This function encodes user information into a base64 string which is id for backend1
def encode_user_info(user_id: int, username: str, email: str) -> str:
    data = {
        "id": user_id,
        "username": username,
        "email": email
    }
    json_str = json.dumps(data)
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    return encoded


# This function decodes the base64 string which is id for backend1 back to user information
def decode_user_info(encoded: str) -> dict:
    decoded_bytes = base64.urlsafe_b64decode(encoded.encode())
    json_str = decoded_bytes.decode()
    data = json.loads(json_str)
    return data


#add bangla translations to airesponse

def add_bangla_translations(airesponse: str) -> str:
    try:

        content = json.loads(airesponse)
        tobe_translated = []
        tobe_translated.append(content['title'])
        tobe_translated.append(content['subtitle'])
        tobe_translated.append(content['description'])

        for i in range(len(content['questions'])):
            question = content['questions'][i]
            
            tobe_translated.append(question['question'])
            tobe_translated.append(question['option1'])
            tobe_translated.append(question['option2'])
            tobe_translated.append(question['option3'])
            tobe_translated.append(question['option4'])
            tobe_translated.append(question['explanation'])


            


        for i in range(len(content['flashcards'])):
            tobe_translated.append(content['flashcards'][i][f'flashcard{i+1}'])
            
        translated_texts = translate_multiple_texts_to_bangla(tobe_translated)

        ind = 0

        content['title-bn'] = translated_texts[ind]
        ind += 1
        content['subtitle-bn'] = translated_texts[ind]
        ind += 1
        content['description-bn'] = translated_texts[ind]
        ind += 1


        content['article-bn'] = translate_bangla_single(content['article'])

        content['questions-bn'] = []
        
        for i in range(len(content['questions'])):
            question = content['questions'][i]
            correct_option_number = 0
            for j in range(4):
                if question['ans'] == question[f'option{j+1}']:
                    correct_option_number = j + 1
                    break

            content['questions-bn'].append({
                "question": translated_texts[ind],
                "option1": translated_texts[ind + 1],
                "option2": translated_texts[ind + 2],
                "option3": translated_texts[ind + 3],
                "option4": translated_texts[ind + 4],
                "explanation": translated_texts[ind + 5],
            })
            ind += 6
            content['questions-bn'][i]['ans'] = content['questions-bn'][i][f'option{correct_option_number}']

        content['flashcards-bn'] = []

        for i in range(len(content['flashcards'])):
            content['flashcards-bn'].append({
                f'flashcard{i+1}': translated_texts[ind],
            })
            ind += 1

        airesponse = json.dumps(content, ensure_ascii=False)
    except Exception as e:
        print(f"Error occurred while adding Bangla translations: {e}")
        airesponse = airesponse

    return airesponse



# This function reduces the text to a maximum number of characters while maintaining the essence of the content.
def reduce_text_distributed(text, max_chars=150000):
    # Step 1: Split text into sentences
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())

    # Step 2: Calculate total characters
    total_chars = sum(len(s) for s in sentences)

    # If already short enough, return as-is
    if total_chars <= max_chars:
        return text

    # Step 3: Proportional sentence trimming
    reduced_sentences = []
    for s in sentences:
        ratio = len(s) / total_chars
        allowed_chars = int(ratio * max_chars)
        words = s.split()

        # If the sentence is longer than allowed, trim it word-wise
        if len(s) > allowed_chars and len(words) > 5:
            # Remove some words to reduce the length proportionally
            factor = allowed_chars / len(s)
            keep_count = max(3, int(len(words) * factor))
            step = len(words) / keep_count

            reduced_words = [words[int(i * step)] for i in range(keep_count)]
            reduced_s = ' '.join(reduced_words)
        else:
            reduced_s = s

        reduced_sentences.append(reduced_s)

    # Step 4: Recombine and truncate just in case
    final_text = ' '.join(reduced_sentences)
    return final_text[:max_chars]