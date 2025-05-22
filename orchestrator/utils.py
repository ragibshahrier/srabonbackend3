from .fayeemai import *

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