from .fayeemai import *
import base64
import json
from deep_translator import GoogleTranslator

def translate_bangla(text: str) -> str:
    """
    Translates the given text to Bangla using Google Translator.
    """
    try:
        translated = GoogleTranslator(source='english', target='bengali').translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text in case of error
    
def smart_translate_bangla(text: str) -> str:
    parts = re.split(r'(?<=[.?!])\s+|\n+', text.strip())
    translated_parts = []
    
    try:
        translator = GoogleTranslator(source='auto', target='bn')
        for part in parts:
            if part.strip():
                translated_parts.append(translator.translate(part.strip()))
        return "\n".join(translated_parts)
    
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback to original text

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
    content = json.loads(airesponse)
    content['title-bn'] = translate_bangla(content['title'])
    content['subtitle-bn'] = translate_bangla(content['subtitle'])
    content['description-bn'] = translate_bangla(content['description'])
    # content['article-bn'] = smart_translate_bangla(content['article'])

    content['questions-bn'] = []
    
    for i in range(len(content['questions'])):
        question = content['questions'][i]
        correct_option_number = 0
        for j in range(4):
            if question['ans'] == question[f'option{j+1}']:
                correct_option_number = j + 1
                break

        content['questions-bn'].append({
            "question": translate_bangla(question['question']),
            "option1": translate_bangla(question['option1']),
            "option2": translate_bangla(question['option2']),
            "option3": translate_bangla(question['option3']),
            "option4": translate_bangla(question['option4']),
        })
        content['questions-bn'][i]['ans'] = content['questions-bn'][i][f'option{correct_option_number}']

    content['flashcards-bn'] = []

    for i in range(len(content['flashcards'])):
        content['flashcards-bn'].append({
            f'flashcard{i+1}': translate_bangla(content['flashcards'][i][f'flashcard{i+1}']),
        })

    airesponse = json.dumps(content, ensure_ascii=False)
    return airesponse