from django.shortcuts import render



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests



from django.http import JsonResponse
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
from .models import StudentProfile

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import IntegrityError, DataError

from django.core.exceptions import ValidationError



# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         print(username)
#         print(password)

#         auth_url = f'{BACKEND3_BASE_URL}auth/jwt/create/'
#         response = requests.post(auth_url, json={"username": username, "password": password})

#         if response.status_code == 200:
#             return Response({
#                 "message": "Login successful",
#                 "token": response.json().get("access")
#             }, status=200)
#         else:
#             return Response({"error": "Invalid credentials"}, status=response.status_code)


# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         auth_url = f'{BACKEND3_BASE_URL}auth/jwt/create/'

#         print(f"Sending login to: {auth_url}")
#         print(f"Payload: {{'username': {username}, 'password': ******}}")

#         try:
#             response = requests.post(auth_url, json={"username": username, "password": password}, timeout=100)
#             print(f"Auth Service Status: {response.status_code}")
#             print(f"Auth Service Response: {response.text}")
#         except requests.exceptions.RequestException as e:
#             print(f"Request to auth service failed: {e}")
#             return Response({"error": "Internal auth request failed"}, status=500)

#         try:
#             data = response.json()
#         except ValueError:
#             return Response({"error": "Auth service did not return JSON", "raw": response.text}, status=500)

#         if response.status_code == 200:
#             return Response({
#                 "message": "Login successful",
#                 "token": data.get("access")
#             }, status=200)
#         else:
#             return Response({"error": data.get("detail", "Login failed")}, status=response.status_code)


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
            "subjects": subjects
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
                student_profile.favsubjects = json.dumps(new_subjects)
            else:
                return Response({"error": "Subjects must be a list"}, status=400)
        # if new_points:
        #     student_profile.points = int(new_points)

        # Save the updated student_profile
        student_profile.save()

        return Response({"message": "Score submitted successfully"}, status=200)
    


class AddCourseView(APIView):
    permission_classes = [IsAuthenticated]

    
        

    def post(self, request):
        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)


        thisstudent = StudentProfile.objects.filter(user=request.user).first()


        course_name = request.data.get('title')  # Assuming the course data is sent in the request body
        # course_description = request.data.get('description')
        course_description = ""
        course_subject = request.data.get('subject')

        try:
            # Make request to backend1 to store this student's course
            

            airesponse = course_generator(cl = thisstudent.level, title = course_name, subject=course_subject)
            airesponse = add_bangla_translations(airesponse)
            response = send_course(backend_id, str(thisstudent.coursenumber), airesponse)

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
        course_id = kwargs.get('course_id')

        username = request.user.username  # The logged-in user's username
        user_id = request.user.id  # The logged-in user's ID (primary key)
        user_email = request.user.id  # The logged-in user's ID (primary key)
        backend_id = encode_user_info(user_id, username, user_email)

        # Find the course with the matching ID
        response = get_course_spec(user_id=backend_id, course_id=course_id)
        if response.status_code == 200:
            course_data = response.json()
            # print(course_data)
            # Assuming the course data is in a field called 'course'
            return JsonResponse(course_data, safe=False)
        else:
            # Handle the case where the course is not found
            return Response({"error": "Course not found"}, status=response.status_code)
        
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

