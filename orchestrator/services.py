from .backend2_client import *
from .backend1_client import *
from .utils import extract_text_from_pdf

def handle_custom_course_creation(request):
    user_id = request.data.get('userId')
    course_title = request.data.get('courseTitle')
    
    if 'pdfs' in request.FILES:
        text = extract_text_from_pdf(request.FILES.getlist('pdfs'))
    else:
        text = request.data.get('text', '')

    ai_data = generate_course_materials(text, course_title)
    store_course(user_id, ai_data)
    return ai_data

def handle_chat(request):
    user_id = request.data.get('userId')
    query = request.data.get('message')
    return get_chat_reply(query)
