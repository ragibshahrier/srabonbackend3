from django.shortcuts import render



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests



from django.http import JsonResponse
from django.http import HttpResponse
from django.views import View
from .wrapper import *
from .fayeemai import *
from .utils import *
# Create your views here.

# BACKEND3_BASE_URL = "http://192.168.0.105:8000/"
# BACKEND3_BASE_URL = "https://srabonbackend3.onrender.com/"
BACKEND3_BASE_URL = os.getenv("BACKEND3_BASE_URL", "https://srabonbackend3.onrender.com/")
if not BACKEND3_BASE_URL.endswith('/'):
    BACKEND3_BASE_URL += '/'  # Ensure it ends with a slash




from rest_framework.views import APIView
from rest_framework.response import Response
from .services import handle_custom_course_creation, handle_chat

from .backend1_client import *


class CustomCourseView(APIView):
    def post(self, request):
        return Response(handle_custom_course_creation(request))

class ChatView(APIView):
    def post(self, request):
        return Response(handle_chat(request))



class StudentCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id  # The logged-in user's ID (primary key)

        try:
            # Make request to backend1 to fetch this student's courses
            backend1_url = f"http://<BACKEND1_IP>:<PORT>/get"
            response = requests.get(backend1_url)

            # If backend1 returns success, forward the data
            if response.status_code == 200:
                return Response(response.json(), status=200)
            else:
                return Response({"error": "Failed to get courses from backend1"}, status=response.status_code)

        except requests.exceptions.RequestException:
            return Response({"error": "Connection to backend1 failed"}, status=500)
        

from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import StudentProfile, Notification

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import IntegrityError, DataError

from django.core.exceptions import ValidationError



class Getserverinfo(APIView):
    def get(self,request):
        stat = checkready()
        if(stat==1):
            return Response({"ready":"True"},status = status.HTTP_200_OK)
        elif(stat==0):
            return Response({"ready":"False"}, status = status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({"ready":"error"}, status = status.HTTP_502_BAD_GATEWAY)

        

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        serializer = TokenObtainPairSerializer(data={"username": username, "password": password})
        if serializer.is_valid():
            return Response({
                "message": "Login successful",
                "token": serializer.validated_data.get("access")
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors.get("non_field_errors", ["Login failed"])[0]},
                status=status.HTTP_401_UNAUTHORIZED
            )

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
        except IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                return Response(
                    {"error": "Username or email already exists."},
                    status=status.HTTP_409_CONFLICT
                )
            return Response(
                {"error": "Database integrity error."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(
                {"error": "Validation error.", "details": e.messages},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except DataError as e:
            return Response(
                {"error": "Data too long or invalid format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Unexpected server error.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = TokenObtainPairSerializer(data={"username": username, "password": password})
        if serializer.is_valid():
            return Response({
                "message": "Registration successful. You are now logged in.",
                "token": serializer.validated_data.get("access")
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Token generation failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class RegisterView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         email = request.data.get('email')

#         if not username or not password or not email:
#             return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.create_user(username=username, password=password, email=email)
#         except IntegrityError:
#             return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = TokenObtainPairSerializer(data={"username": username, "password": password})
#         if serializer.is_valid():
#             return Response({
#                 "message": "Registration successful. You are now logged in.",
#                 "token": serializer.validated_data.get("access")
#             }, status=status.HTTP_201_CREATED)
#         else:
#             return Response({"error": "Token generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class StudentDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username  # The logged-in user's username
        userid = request.user.id
        email = request.user.email  # The logged-in user's email
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        if not student_profile:
            return Response({"error": "Student profile not found"}, status=404)
        
        name = student_profile.name
        level = student_profile.level
        points = student_profile.points
        subjects = student_profile.favsubjects
        subjects = json.loads(subjects) if subjects else []
        quiz_score = student_profile.quiz_score
        quiz_attempts = student_profile.quiz_attempts
        quiz_highest_score = student_profile.quiz_highest_score
        quiz_average_score = quiz_score / quiz_attempts if quiz_attempts > 0 else 0
        total_courses = 0
        course_completed = 0
        course_pending = 0

        if isinstance(subjects, list):
            subjects = list(set([s.capitalize() for s in subjects]))


        response = get_all_course_progress(user_id=encode_user_info(user_id=userid, username=username, email=userid))
        if response.status_code != 200:
            return Response({"error": "Failed to retrieve course progress"}, status=response.status_code)
        course_progress = response.json()
        course_progress = course_progress.get('course_progress_list', [])
        
        for course in course_progress:
            # "description_read": progress.get("description_read", 0),
            # "flashcards_read": progress.get("flashcards_read", 0),
            # "articles_read": progress.get("articles_read", 0),
            # "quiz_score": progress.get("quiz_score", 0),
            # "previous_answers": progress.get("previous_answers", ""),
            total_courses += 1
            if course.get("description_read", 0) > 0 and course.get("flashcards_read", 0) > 0 and course.get("articles_read", 0) > 0 and course.get("quiz_score", 0) > 0 and course.get("previous_answers", "") != "":
                course_completed += 1

        course_pending = total_courses - course_completed


        print(f"Authenticated student's username: {username}")
        print(f"Authenticated student's ID: {userid}")
        # res = get_course_list("user123")
        # print(f"Course list: {res.json()}")

        resp = {
            "username": username,
            "userid": userid,
            "email": email,
            "name": name,
            "class": level,
            "points": points,
            "subjects": subjects,
            "quiz_score": quiz_score,
            "quiz_attempts": quiz_attempts,
            "quiz_highest_score": quiz_highest_score,
            "quiz_average_score": quiz_average_score,
            "total_courses": total_courses,
            "course_completed": course_completed,
            "course_pending": course_pending
        }
        return Response(resp, status=200)
    
    def post(self, request):
        user_id = request.user.id
        username = request.user.username
        email = request.user.email

        # course_id = request.data.get('courseId')
        # score = request.data.get('score')
        # print(f"User ID: {user_id}, Course ID: {course_id}, Score: {score}")

        # Filter the StudentProfile model using the username
        student_profile = StudentProfile.objects.filter(user=request.user).first()

        if not student_profile:
            return Response({"error": "Student profile not found"}, status=404)

        # Perform any additional operations with the student_profile instance here
        # Update the email and level fields of the student_profile
        # new_email = request.data.get('email')
        new_level = request.data.get('class')
        new_name = request.data.get('name')
        new_subjects = request.data.get('subjects', [])
        # new_points = request.data.get('points')

        if new_name:
            student_profile.name = new_name
        if new_level:
            student_profile.level = int(new_level)
        if new_subjects:
            # Ensure new_subjects is a list and convert it to a JSON string
            if isinstance(new_subjects, list):
                new_subjects = list(set([s.capitalize() for s in new_subjects]))
                student_profile.favsubjects = json.dumps(new_subjects)
            else:
                return Response({"error": "Subjects must be a list"}, status=400)
        # if new_points:
        #     student_profile.points = int(new_points)

        # Save the updated student_profile
        student_profile.save()

        return Response({"message": "Profile updated successfully"}, status=200)
    



class AddCourseView(APIView):
    permission_classes = [IsAuthenticated]

    
        

    def post(self, request):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)


        thisstudent = StudentProfile.objects.filter(user=request.user).first()


        


        if request.content_type.startswith('application/json'):
            course_name = request.data.get('title')  # Assuming the course data is sent in the request body
            course_subject = request.data.get('subject')
            pdf_file = None  # no file can be sent via JSON
        else:
            course_name = request.POST.get('title')
            course_subject = request.POST.get('subject')
            pdf_file = request.FILES.get('file')

        full_text = ""

        if pdf_file:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
            except Exception as e:
                return Response({"error": "PDF processing failed"}, status=500)
            
        MAX_CHAR_LIMIT = 150000

        full_text = reduce_text_distributed(full_text, MAX_CHAR_LIMIT)
            
        try:
            # Make request to backend1 to store this student's course
            

            airesponse = course_generator(cl = thisstudent.level, title = course_name, subject=course_subject, pdftext=full_text)
            airesponse = add_bangla_translations(airesponse)
            response = send_course(user_id=backend_id, author_name=username, name=str(thisstudent.coursenumber), parent=airesponse)

            thisstudent.coursenumber += 1
            thisstudent.save()

            # backend1_url = f"http://<BACKEND1_IP>:<PORT>/courses/"
            # response = requests.post(backend1_url, json={
            #     "userId": user_id,
            #     "course": course_data
            # })
            # print(airesponse)
            # airesponse_text = airesponse.get('text', 'No response text available')
            # print(f"AI Response Text: {airesponse_text}")

            

            # If backend1 returns success, forward the data
            if response.status_code == 200:
                level = thisstudent.level
                print(f"Student's level: {level}")
                print(f"Course name: {course_name}")
                # airesponse = creating_time_course_generation([course_name],level)
                # print(airesponse)

                return Response(response.json(), status=200)
            else:
                return Response({"error": "Failed to add course in backend1"}, status=response.status_code)
        except requests.exceptions.RequestException:
            return Response({"error": "Connection to backend1 failed"}, status=500)


class CoursesView(APIView):
    permission_classes = [IsAuthenticated]

        
    def get(self, request, *args, **kwargs):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)


        course_id = kwargs.get("course_id")
        if course_id:
            response = get_course_spec(user_id=backend_id, course_id=str(course_id))
            if response.status_code == 200:
                course_data = response.json()
                course_data = course_data['course']['parent']
                course_data = json.loads(course_data)
                # print(course_data)
                # Assuming the course data is in a field called 'course'
                return JsonResponse(course_data, safe=False)
            else:
                # Handle the case where the course is not found
                return Response({"error": "Course not found"}, status=response.status_code)

        response = get_course_list(backend_id)
        objectt = response.json()  # Convert the response to a Python object (dictionary or list)
        objectt = objectt['courses']

        
        objects = []

        # objects.append(json.loads(objectt[0]['parent']))
        # objects.append(json.loads(objectt[1]['parent']))
        # print(len(objectt))

        for i in range(len(objectt)):
            objectt[i]['parent'] = json.loads(objectt[i]['parent'])
        
        
        objectt2 = [
            {
                "name":11,
                "subject": "Math",
                "title": "Calculus",
                "description": "An introduction to derivatives, integrals, and the foundational concepts of calculus."
            },{
                "name":12,
                "subject": "Math",
                "title": "Calculus",
                "description": "An introduction to derivatives, integrals, and the foundational concepts of calculus."
            },{
                "name":13,
                "subject": "Math",
                "title": "Calculus",
                "description": "An introduction to derivatives, integrals, and the foundational concepts of calculus."
            },
            
            {

                "name":14,
                "subject": "Science",
                "title": "Physics",
                "description": "Covers motion, forces, energy, and basic mechanics."
            },{
                "name":15,
                "subject": "Science",
                "title": "Physics",
                "description": "Covers motion, forces, energy, and basic mechanics."
            },{
                "name":16,
                "subject": "Science",
                "title": "Physics",
                "description": "Covers motion, forces, energy, and basic mechanics."
            },
            
            
            {

                "name":17,      
                "subject": "Computer Science",
                "title": "Data Structures",
                "description": "Learn about arrays, linked lists, trees, stacks, queues, and more."
            },{
                "name":18,
                "subject": "Computer Science",
                "title": "Data Structures",
                "description": "Learn about arrays, linked lists, trees, stacks, queues, and more."
            },{
                "name":19,
                "subject": "Computer Science",
                "title": "Data Structures",
                "description": "Learn about arrays, linked lists, trees, stacks, queues, and more."
            },

            {

"name":20,                "subject": "English",
                "title": "Creative Writing",
                "description": "Explore storytelling, poetry, and developing your own voice as a writer."
            },{
                "name":21,
                "subject": "English",
                "title": "Creative Writing",
                "description": "Explore storytelling, poetry, and developing your own voice as a writer."
            },{
                "name":22,
                "subject": "English",
                "title": "Creative Writing",
                "description": "Explore storytelling, poetry, and developing your own voice as a writer."
            },

            {

"name":23,                "subject": "History",
                "title": "World War II",
                "description": "A detailed look into the causes, events, and consequences of WWII."
            },{
                "name":24,
                "subject": "History",
                "title": "World War II",
                "description": "A detailed look into the causes, events, and consequences of WWII."
            },{
                "name":25,
                "subject": "History",
                "title": "World War II",
                "description": "A detailed look into the causes, events, and consequences of WWII."
            },
            {
                "name":26,
                "subject": "Biology",
                "title": "Cell Biology",
                "description": "Study the structure and function of cells and cellular components."
            },{
                "name":27,
                "subject": "Biology",
                "title": "Cell Biology",
                "description": "Study the structure and function of cells and cellular components."
            },{
                "name":28,
                "subject": "Biology",
                "title": "Cell Biology",
                "description": "Study the structure and function of cells and cellular components."
            },
            {
                "name":29,
                "subject": "Chemistry",
                "title": "Organic Chemistry",
                "description": "Focus on the structure, properties, and reactions of organic compounds."
            },{
                "name":30,
                "subject": "Chemistry",
                "title": "Organic Chemistry",
                "description": "Focus on the structure, properties, and reactions of organic compounds."
            },{
                "name":31,
                "subject": "Chemistry",
                "title": "Organic Chemistry",
                "description": "Focus on the structure, properties, and reactions of organic compounds."
            },
            {
                "name":32,
                "subject": "Economics",
                "title": "Microeconomics",
                "description": "Introduction to supply and demand, consumer behavior, and market structures."
            },{
                "name":33,
                "subject": "Economics",
                "title": "Microeconomics",
                "description": "Introduction to supply and demand, consumer behavior, and market structures."
            },{
                "name":34,
                "subject": "Economics",
                "title": "Microeconomics",
                "description": "Introduction to supply and demand, consumer behavior, and market structures."
            },
            {
                "name":35,
                "subject": "Philosophy",
                "title": "Ethics",
                "description": "Explore moral theories and ethical dilemmas in modern society."
            },{
                "name":36,
                "subject": "Philosophy",
                "title": "Ethics",
                "description": "Explore moral theories and ethical dilemmas in modern society."
            },{
                "name":37,
                "subject": "Philosophy",
                "title": "Ethics",
                "description": "Explore moral theories and ethical dilemmas in modern society."
            },
            
            
            {

"name":37,                "subject": "Programming",
                "title": "Python Basics",
                "description": "Start programming with Python: syntax, variables, loops, and functions."
            },{
                "name":138,
                "subject": "Programming",
                "title": "Python Basics",
                "description": "Start programming with Python: syntax, variables, loops, and functions."
            },{
                "name":639,
                "subject": "Programming",
                "title": "Python Basics",
                "description": "Start programming with Python: syntax, variables, loops, and functions."
            },
        ]
        
        
        return JsonResponse(objectt, safe=False)
    





  
class ChatConvo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        message = request.data.get('message')
        limit = request.data.get('limit', 'true')  # Default to "true" if not provided

        if (limit == "false"):
            # Call the delete_chat function from wrapper.py
            response = delete_message(backend_id)
            

        receiver = "ai"
        # timestamp = request.data.get('timestamp')

        # Call the send_chat function from wrapper.py
        response = send_chat(backend_id, receiver, message)

        contexts = get_chats(backend_id, receiver, 10)
        contexts = contexts.json()
        contexts = contexts['messages']

        message_of_ai = chat_bot(contexts, message)

        receiver = backend_id

        response = send_chat(backend_id, receiver, message_of_ai)

        airesponse = {
            "message": message_of_ai,
            "sender": "ai",
            "receiver": user_id,
            "timestamp": response.json().get('Timestamp')
        }



        if response.status_code == 200:
            return Response(airesponse, status=200)
        else:
            return Response({"error": "Failed to send chat"}, status=response.status_code)




class ScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        delta_score = request.data.get('delta_score')

        profile = StudentProfile.objects.filter(user=user).first()

        # Update the user's points in the database
        profile.points += delta_score
        profile.save()

        return Response({"message": "Score updated successfully", "score":profile.points}, status=200)
    
    def get(self, request):
        user = request.user
        # Get the user's current score from the database
        profile = StudentProfile.objects.filter(user=user).first()
        current_score = profile.points

        return Response({"score": current_score}, status=200)
    

class AllStudentsProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all student profiles
        student_profiles = StudentProfile.objects.exclude(user__username='admin').order_by('-points')

        # Serialize the profiles into a list of dictionaries
        profiles_data = []
        for profile in student_profiles:
            profiles_data.append({
                "username": profile.user.username,
                "name": profile.name,
                "score": profile.points,
                "class": profile.level,
            })

        return Response(profiles_data, status=200)





class CourseContentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id, lang="en"):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        response = get_course_spec(user_id=backend_id, course_id=course_id)

        data = response.json()
        data = data['course']['parent']
        data = json.loads(data)
        # print(type(data))
        # with open("testdict", "w", encoding="utf-8") as f:
        #     f.write(str(data))
        # data = dict
        # # print(data)
        # create_pdf(data, "test.pdf")
        # return Response({"message": "PDF created successfully"}, status=200)
        try:
            if(lang=="en"):
                pdf_buffer = createPdf_with_HTTP_response(data)
            else:
                pdf_buffer = createPdf_with_HTTP_response_bangla(data)
            response = HttpResponse(
                pdf_buffer, 
                content_type='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="o.pdf"'
                }
            )
            return response
        except Exception as e:
            return Response({"error": "Failed to create PDF", "details": str(e)}, status=500)
        

class PersonalCourseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's email
        backend_id = encode_user_info(user_id, username, user_email)
        studentProfile = StudentProfile.objects.filter(user=request.user).first()

        # Get the user's course progress for the specified course
        course_progress = get_course_progress(user_id=backend_id, courseID=course_id)
        if course_progress.status_code != 200:
            return Response({"error": "Failed to retrieve course progress"}, status=course_progress.status_code)
        
        course_progress = course_progress.json()
        if 'progress' not in course_progress:
            return Response({"error": "Course progress not found"}, status=404)
        
        course_progress = course_progress['progress']

        return Response(course_progress, status=200)
    
    def post(self, request, course_id):
        username = request.user.username
        user_id = request.user.id
        user_email = request.user.id
        backend_id = encode_user_info(user_id, username, user_email)
        studentProfile = StudentProfile.objects.filter(user=request.user).first()
        # Get the user's course progress for the specified course
        course_progress = get_course_progress(user_id=backend_id, courseID=course_id)
        course_progress = course_progress.json()
        course_progress = course_progress['progress']

        data = request.data

        # progress = {
        #     "description_read":course.get("description_read", 0),
        #     "flashcards_read": course.get("flashcards_read", 0),
        #     "articles_read": course.get("articles_read", 0),
        #     "quiz_score": course.get("quiz_score", 0),
        #     "previous_answers": course.get("previous_answers", ""),
        # }

        course_progress["description_read"] = data.get("description_read", course_progress.get("description_read", 0))
        course_progress["flashcards_read"] = data.get("flashcards_read", course_progress.get("flashcards_read", 0))
        course_progress["articles_read"] = data.get("articles_read", course_progress.get("articles_read", 0))
        course_progress["quiz_score"] = data.get("quiz_score", course_progress.get("quiz_score", 0))
        course_progress["previous_answers"] = data.get("previous_answers", course_progress.get("previous_answers", ""))

        if course_progress["previous_answers"] !="":
            studentProfile.quiz_score += course_progress["quiz_score"]
            studentProfile.quiz_attempts += 1
            studentProfile.quiz_highest_score = max(studentProfile.quiz_highest_score, course_progress["quiz_score"])
            studentProfile.save()


        if "previous_answers" in course_progress and isinstance(course_progress["previous_answers"], str):
            course_progress["previous_answers"] = course_progress["previous_answers"].replace(" ", "").upper()

        response = send_course_progress(user_id=backend_id, courseID=course_id, course_progress=course_progress)
        # Update the user's course progress in the database
        if response.status_code == 200:
            return Response({"message": "Course progress updated successfully"}, status=200)
        else:
            return Response({"error": "Failed to update course progress"}, status=response.status_code)
        

class NotificationView(APIView):
    def get(self, request, arg):
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-timestamp')

        if arg == "all":
            notifications_data = [
                {
                    "id": notification.unique_id,
                    "message": notification.message,
                    "timestamp": notification.timestamp.isoformat(),
                    "is_read": notification.is_read
                } for notification in notifications
            ]
            return Response(notifications_data, status=200)
        
        elif arg == "unread":
            unread_notifications = notifications.filter(is_read=False)
            unread_notifications_data = [
                {
                    "id": notification.unique_id,
                    "message": notification.message,
                    "timestamp": notification.timestamp.isoformat(),
                    "is_read": notification.is_read
                } for notification in unread_notifications
            ]
            return Response(unread_notifications_data, status=200)
        
        elif arg.isdigit():
            quantity = int(arg)
            if quantity <= 0:
                return Response({"error": "Quantity must be a positive integer"}, status=400)
            recent_notifications = notifications[:quantity]
            recent_notifications_data = [
                {
                    "id": notification.unique_id,
                    "message": notification.message,
                    "timestamp": notification.timestamp.isoformat(),
                    "is_read": notification.is_read
                } for notification in recent_notifications
            ]
            return Response(recent_notifications_data, status=200)
        
        else:
            return Response({"error": "Invalid argument"}, status=400)
    
    def post(self, request, arg):
        user = request.user
        
        if arg=="make":
            message = request.data.get('message')
            if not message:
                return Response({"error": "Message is required"}, status=400)

            notification = Notification(user=user, message=message)
            notification.save()
            return Response({"message": "Notification created", "id": notification.unique_id}, status=201)
        elif arg == "supermake":
            if not user.is_superuser:
                return Response({"error": "Permission denied. Only superusers can create this notification."}, status=403)
            message = request.data.get('message')
            if not message:
                return Response({"error": "Message is required"}, status=400)
            # Create a notification for all users
            users = User.objects.all()
            for user in users:
                # Create a notification for each user    
                notification = Notification(user=user, message=message)
                notification.save()

            
            return Response({"message": "Superuser notification created", "id": notification.unique_id}, status=201)
        
        
        
    def put(self, request, arg):
        user = request.user
        
        if arg == "readall":
            Notification.objects.filter(user=user, is_read=False).update(is_read=True)
            return Response({"message": "All notifications marked as read"}, status=200)

        notification_id = request.data.get('id')

        if not notification_id:
            return Response({"error": "Notification ID is required"}, status=400)

        try:
            notification = Notification.objects.get(unique_id=notification_id, user=user)
            if arg == "read":
                notification.is_read = True
                notification.save()
                return Response({"message": "Notification marked as read"}, status=200)
            elif arg == "unread":
                notification.is_read = False
                notification.save()
                return Response({"message": "Notification marked as unread"}, status=200)
            elif arg == "delete":
                notification.delete()
                return Response({"message": "Notification deleted"}, status=200)
            else:
                return Response({"error": "Invalid action"}, status=400)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)
    
    def delete(self, request, arg):
        user = request.user
        
        if arg == "all":
            Notification.objects.filter(user=user).delete()
            return Response({"message": "All notifications deleted"}, status=200)
        
        elif arg == "read":
            Notification.objects.filter(user=user, is_read=True).delete()
            return Response({"message": "All read notifications deleted"}, status=200)



"""Adds a course from the explorer view"""
class AddFromExplorerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        course_id = request.data.get('courseId')
        if not course_id:
            return Response({"error": "Course ID is required"}, status=400)

        response = send_explorer_course(user_id=backend_id, courseID=course_id)
        if response.status_code != 200:
            return Response({"status": "Failed to add course"}, status=response.status_code)

        else:
            # responds with status succcess with status code 200
            return Response(response.json(), status=200)
        
"""Makes a course public or private"""
class CourseAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, access):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        course_id = request.data.get('courseId')

        if not course_id:
            return Response({"error": "Course ID is required"}, status=400)

        if(access == "public"):
            # Call the function to make the course public
            response = set_course_public(user_id=backend_id, course_id=course_id)
        elif(access == "private"):
            # Call the function to make the course private
            response = set_course_private(user_id=backend_id, course_id=course_id)
        
        else:
            return Response({"error": "Invalid access type"}, status=400)
        

        

        if response.status_code != 200:
            return Response({"status": "Failed to make course public"}, status=response.status_code)

        else:
            # responds with status succcess with status code 200
            return Response(response.json(), status=200)
        

class ExplorerCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        response = get_explorer_courses(user_id=backend_id)

        if response.status_code == 200:
            courses_data = response.json()

            courses_data = courses_data['courses']
            for i in range(len(courses_data)):
                try:
                    courses_data[i]['parent'] = json.loads(courses_data[i]['parent'])
                except json.JSONDecodeError:
                    courses_data[i]['parent'] = {"error": "Invalid JSON format in course data"}

            return Response(courses_data, status=200)
        else:
            return Response({"error": "Failed to retrieve explorer courses"}, status=response.status_code)
        


class GrammarHelperView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        text = request.data.get('text')
        if not text:
            return Response({"error": "Text is required"}, status=400)
        
        task = request.data.get('task')
        if task not in ['grammar_check', 'paraphrase', 'summarize']:
            return Response({"error": "Invalid task. Must be 'grammar_check' or 'spell_check'"}, status=400)

        response = None
        if task == 'grammar_check':
            # Call the grammar_check function from wrapper.py
            response = grammar_corrector(text)
        elif task == 'paraphrase':
            # Call the para_phrase function from wrapper.py
            response = paraphraser(text)
        elif task == 'summarize':
            # Call the summarizer function from wrapper.py
            response = summarizer(text)

        if(response is None):
            return Response({"error": "something went wrong"}, status=400)
        # response = grammar_check(text)
        if response.status_code == 200:
            return Response(response, status=200)
        else:
            return Response({"error": "Failed to check grammar"}, status=200)
        
