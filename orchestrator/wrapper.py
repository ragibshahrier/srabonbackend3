import requests
import json
from datetime import datetime
import os

# BASE_URL = 'http://localhost:5000/'  # Replace with your backend URL
# BASE_URL = "http://192.168.0.105:5000"  # Replace with "http://localhost:5000" or your local IP
# BASE_URL = "https://srabonbackend1.onrender.com"  # Replace with "http://localhost:5000" or your local IP
BASE_URL = os.getenv("BACKEND1_BASE_URL", "https://srabonbackend1.onrender.com")

if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]  # Remove trailing slash if present

def checkready():
    try:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36'
        }
        r = requests.get(BASE_URL, headers=headers, timeout=10)
        if r.status_code == 200 and r.text.strip() == 'Ahis':
            return 1
        else:
            return 0
    except requests.exceptions.RequestException as e:
        return -1

def send_explorer_course(user_id, courseID):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "courseadd2",
        "user_id": str(user_id),
        "courseID": courseID
    })


def send_course(user_id,author_name ,name, parent):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "courseadd",
        "user_id": str(user_id),
        "author_name" : author_name,
        "name": name,
        "parent": parent, # parent === description
    })

def send_chat(user_id, receiver, message, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "chatadd",
        "user_id": str(user_id),
        "receiver": receiver,
        "message": message,
        "timestamp": timestamp
    })

def send_flashcard(user_id, course, content):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "flashadd",
        "user_id": str(user_id),
        "course": course,
        "content": content
    })

def send_question(user_id, course, question, options, correct, explanation):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "quesadd",
        "user_id": str(user_id),
        "course": course,
        "question": question,
        "option1": options[0],
        "option2": options[1],
        "option3": options[2],
        "option4": options[3],
        "ans": correct,
        "explanation": explanation
    })

def send_article(user_id, course, title, content):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "articleadd",
        "user_id": str(user_id),
        "course": course,
        "title": title,
        "content": content
    })

def send_status(user_id):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "createstatus",
        "user_id": str(user_id)
    })

def send_course_progress(user_id, courseID, course_progress):
    return requests.post(f"{BASE_URL}/send", json={
        "mode": "courseprogress",
        "user_id": str(user_id),
        "courseID": courseID,
        "course_progress": course_progress
    })

def get_chats(user_id, receiver, count=10):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "chatget",
        "user_id": str(user_id),
        "receiver": receiver,
        "count": count
    })

def get_questions(user_id, course, qlist):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "quesget",
        "user_id": str(user_id),
        "course": course,
        "qlist": ",".join(str(q) for q in qlist)
    })

def get_flashcards(user_id, course, flist):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "flashget",
        "user_id": str(user_id),
        "course": course,
        "flist": ",".join(str(f) for f in flist)
    })

def get_article(course, article_id):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "articleget",
        "course": course,
        "articleID": article_id
    })

def get_explorer_courses(user_id):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "coursegetexplorer",
        "user_id": str(user_id)
    })

def get_course_progress(user_id, courseID):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "coursegetprogress",
        "user_id": str(user_id),
        "courseID": courseID
    })

def get_all_course_progress(user_id):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "coursegetprogressall",
        "user_id": str(user_id),
    })

def mark_question_solved(user_id, question_id):
    return requests.post(f"{BASE_URL}/process", json={
        "mode": "quesprocess",
        "function": "solved",
        "user_id": str(user_id),
        "questionID": question_id
    })

def mark_flashcard_read(user_id, flashcard_id):
    return requests.post(f"{BASE_URL}/process", json={
        "mode": "flashprocess",
        "function": "read",
        "user_id": str(user_id),
        "flashcardID": flashcard_id
    })

def mark_article_read(user_id, article_id):
    return requests.post(f"{BASE_URL}/process", json={
        "mode": "articleprocess",
        "function": "read",
        "user_id": str(user_id),
        "articleID": article_id
    })

def delete_message(user_id):
    return requests.post(f"{BASE_URL}/process", json={
        "mode": "msgdelete",
        "user_id": str(user_id)
    })

def get_course_list(user_id):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "courseget",
        "user_id": str(user_id)
    })

def get_course_spec(user_id, course_id):
    return requests.post(f"{BASE_URL}/get", json={
        "mode": "coursegetspec",
        "user_id": str(user_id),
        "courseID": course_id
    })

def set_course_public(user_id,course_id):
    return requests.post(f"{BASE_URL}/process", json={
        "mode": "setPublic",
        "user_id": str(user_id),
        "courseID": course_id
    })

def set_course_private(user_id, course_id):
    return requests.post(f"{BASE_URL}/process", json={
        "mode": "setPrivate",
        "user_id": str(user_id),
        "courseID": course_id
    })

