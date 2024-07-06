
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse

from parser.models import Resume_data
# from .forms import ResumeForm

# F
from parser.forms import UserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout, login as auth_login
from django.contrib.auth.decorators import login_required
from .decorators import superuser_required
from django.http.response import HttpResponseRedirect
from parser.functions import generate_form_errors
import json

from pdfminer.high_level import extract_text
import tempfile
import os
import google.generativeai as genai

# YOUR GEMINI API KEY REQUIRED 
genai.configure(api_key="AIzaSyCgl_43mq1pS7bByNd82Y5h7OtlFdRPgIk")
model = genai.GenerativeModel('gemini-pro')


def index(request):
    return render(request,'index_m.html')


def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')


def convert_to_text(file_path):
    text = extract_text(file_path)
    return text


@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file.close()
            temp_file_path = temp_file.name

        # resume = Resume.objects.get(id=resume.id)
        converted_text = convert_to_text(temp_file_path)

        # Delete the temporary file after use
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        print("converted_text =", converted_text)
        prompt = converted_text + """You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
1. name
2. email
3. number
5. years of work experience 0 if none
6. technical skills seperated by comma
as a dictionary with key name, email, number, experience(number of years), skills \n always use these keys if a value is not there return null but still return in these keys"""

        response = model.generate_content(prompt)
        gemini_responses = response.candidates[0].content.parts[0].text
        try:
            print(gemini_responses)
            data = json.loads(f"""{gemini_responses}""")
        except json.JSONDecodeError as e:
            print("JSON decode error:", str(e))
            context = {
                'error': 'Failed to parse response, Try again'}
            return render(request, 'upload_m.html', context=context)

        Resume_data.objects.create(
            name=data['name'],
            email=data['email'],
            number=data['number'],
            experience=int(data['experience']),
            skills=data['skills'],
            file = uploaded_file,
            user=request.user,
        )
        return redirect('parser:view_resume')
    else:
        try:
            uploaded_item = Resume_data.objects.get(user=request.user)
            context = {
                "uploaded": True
            }
        except:
            context = {
                "uploaded": False
            }
    return render(request, 'upload_m.html', context=context)

def upload_success(request):
    try:
        # Example: Retrieve the latest uploaded resume
        latest_resume = Resume.objects.latest('id')  # Adjust this query as per your application logic
        return render(request, 'success.html', {'resume': latest_resume})
    except Resume.DoesNotExist:
        return render(request, 'success.html', {'resume': None})

@login_required
# def view_all(request, id):
def view_resume(request):
    # Retrieve the resume object
    # table = Resume_data.objects.all()
    try:
        resume = Resume_data.objects.get(user=request.user)
        # print("showing",resume.skills)
        context = {
            # 'resume_data' : table,
            'resume': resume
        }
        return render(request, 'view_resume.html', context=context)
    except Resume_data.DoesNotExist:
        return HttpResponse("Resume not found", status=404)
    
    
@login_required
@superuser_required
def view_all(request):
    # Retrieve the resume object
    resume = Resume_data.objects.all()
    try:
        context = {
            # 'resume_data' : table,
            "resume_data": resume
        }
        return render(request, 'view_all.html', context=context)
    except Resume_data.DoesNotExist:
        return HttpResponse("Resume not found", status=404)

def delete(request, id):
    item = Resume_data.objects.get(pk=id)
    item.delete()

    # page path from which request is made ( delete is clicked )
    referer = request.META.get('HTTP_REFERER', '')

    if 'view_resume'in referer:
        return redirect('parser:upload_resume')
    else:
        return redirect('parser:view_all')

# F 
def auth(request):
    if request.method == "POST":
        intension = request.POST.get('intension')
        if intension == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    return HttpResponseRedirect("/view_all/")
                else:
                    return HttpResponseRedirect("/upload/")
            else:
                form = UserForm()
                context = {
                    "error2" : True,
                    "form": form,
                    "message" : "Invalid username or password",
                    "active_side": ""
                }
                return render(request, "auth_F.html", context=context)
            

        # signup 
        form = UserForm(request.POST)
        raw_password = request.POST.get('password')
        if len(raw_password) < 8 :
            form = UserForm()
            context = {
                "error" : True,
                "form": form,
                "message" : "Password is too short!!",
                "active_side": "right-panel-active"
            }
            return render(request, "auth_F.html", context=context)
            
        if form.is_valid():
            instance = form.save(commit=False)

            user = User.objects.create_user(
                username = instance.username,
                password = instance.password,
                email = instance.email,
            )

            user = authenticate(request, username=instance.username, password = instance.password)
            auth_login(request, user)

            return HttpResponseRedirect("/upload/")
        else:
            message = generate_form_errors(form)
            print("error-message", message)
            form = UserForm()
            context = {
                "title" : "Signup",
                "error" : True,
                "message" : message,
                "form" : form,
                "active_side": "right-panel-active"
            }
            return render(request, "auth_F.html", context = context)
    else:
        form = UserForm()
        context = {
            "form": form,
            "active_side": "right-panel-active"
        }
        return render(request, "auth_F.html", context=context)
    
def logout_view(request):
    logout(request)
    return redirect('parser:auth')