from django.shortcuts import render, redirect
from django.http import JsonResponse
from openai import OpenAI

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

from transformers import pipeline  



chatbot_pipeline = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")

conversations = {}
def ask_huggingface(message,user_id):
    # Generate a response with Hugging Face model
    try:
        responses = chatbot_pipeline(message, 
                                     max_new_tokens=100, 
                                     num_return_sequences=1   
                                     #truncation=True,           # truncate input if too long
                                     #pad_token_id=chatbot_pipeline.tokenizer.eos_token_id  # set padding token if needed
                                     )
        answer = responses[0]['generated_text'].strip()
        return answer
    except Exception:
        return "Sorry, I couldn't process your message at the moment."
   

    


# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        #response = ask_openai(message)
        if not request.user.is_authenticated:
        # Redirect to login or handle anonymous user
            return redirect('login')
    
        user_id = str(request.user.id)  # String or integer user ID
    # Use user_id to track conversation or personalize data
        #user_id = str(request.user.id)  # unique user id to track conversation
        response = ask_huggingface(message,user_id)
        #response = ask_huggingface(message,user.id)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')