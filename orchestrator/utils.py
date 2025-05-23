from .fayeemai import *
import base64
import json

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

def encode_user_info(user_id: int, username: str, email: str) -> str:
    data = {
        "id": user_id,
        "username": username,
        "email": email
    }
    json_str = json.dumps(data)
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    return encoded

def decode_user_info(encoded: str) -> dict:
    decoded_bytes = base64.urlsafe_b64decode(encoded.encode())
    json_str = decoded_bytes.decode()
    data = json.loads(json_str)
    return data