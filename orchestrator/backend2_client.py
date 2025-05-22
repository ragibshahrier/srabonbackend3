import requests

BACKEND2_BASE_URL = "http://localhost:8002/api"

def generate_course_materials(clean_text, title):
    return requests.post(f"{BACKEND2_BASE_URL}/generate", json={
        "text": clean_text,
        "courseTitle": title
    }).json()

def get_chat_reply(query, context=None):
    return requests.post(f"{BACKEND2_BASE_URL}/chat", json={
        "query": query,
        "context": context or ""
    }).json()
