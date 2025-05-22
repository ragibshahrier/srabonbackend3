import requests

BACKEND1_BASE_URL = "http://localhost:8001/api"

def store_course(user_id, course_data):
    return requests.post(f"{BACKEND1_BASE_URL}/courses/", json={
        "userId": user_id,
        "course": course_data
    }).json()

def save_quiz_result(user_id, course_id, score):
    return requests.post(f"{BACKEND1_BASE_URL}/quiz/submit", json={
        "userId": user_id,
        "courseId": course_id,
        "score": score
    }).json()
