from django.shortcuts import render, redirect
from django.http import JsonResponse
from openai import OpenAI

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

from transformers import pipeline  



#openai_api_key = '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'
#openai.api_key = openai_api_key
#set OPENAI_API_KEY=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
#set OPENAI_API_KEY=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
# client = OpenAI(api_key=openai_api_key)
# def ask_openai(message):

#     try: 
#         response = client.chat.completions.create(
#         #model="gpt-3.5-turbo",
#         model="gpt-oss-120b",
#         messages=[
#                 {"role": "system", "content": "You are an helpful assistant."},
#                 {"role": "user", "content": message},
#             ],
#         max_tokens=100,
#         temperature=0.7,
#     )
        
#         answer = response.choices[0].message.content.strip()
#         return answer
#     except:
#         return "API quota exceeded. Please try again later."

# Initialize Hugging Face conversational pipeline once (CPU usage)
#chatbot_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")

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
    #try:
    # chat_history = conversations.get(user_id, "")
    # #input_text = chat_history + "\nUser: " + message + "\nBot:"
    # input_text = message

    # response = chatbot_pipeline(
    #     input_text,
    #     max_new_tokens=100,
    #     pad_token_id=chatbot_pipeline.tokenizer.eos_token_id
    # )

        
    # reply = response[0]['generated_text'].strip()
    # # Update history
    # conversations[user_id] = input_text + reply + "\n"
    # return reply
        # your chatbot generation code here
        #response = ...  # generate response
        # if not response:
        #     return "Sorry, I couldn't generate a response."
        # return response


    # except Exception:
    #     return "Sorry, something went wrong. Please try again."

    


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