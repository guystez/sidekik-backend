
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from searchfeature.models import Conversation
from searchfeature.register import NewUserForm
from searchfeature.serializers import AnswersSerializer, CartSerializer, CartSerializertwo, ChatroomSerializer, ConversationSerializer, OpenersSerializer, QuestionsSerializer
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import stripe
from django.views.decorators.csrf import csrf_exempt
import users
from .models import Answer, Cart_new, Cart_openers, ChatMessage, Chatroom, Openers, Questions
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.messages import error, success
import re
import random
from django.utils.decorators import method_decorator
from django.views import View



@api_view(['POST'])
def insert_db(request):
    info_to_db = request.data.get('info_to_db')
    conversation = Conversation(chat=info_to_db)
    conversation.save()
    return Response({"status": "success"})



@api_view(['POST'])
def insert_db_openers(request):
    info_to_db = request.data.get('info_to_db')
    conversation = Openers(opener=info_to_db)
    conversation.save()
    return Response({"status": "success"})



last_similar_indices = []
limited_inputs = []
input_check = []
# @login_required
@api_view(['POST'])
def search(request):
    
    global last_similar_indices,input_check
    customer_input = request.data.get('customer_input')
    print(customer_input,'customer_input')
    input_check.append(customer_input)
    
    # Check if the input has changed

    # if len(input_check) >= 4 and customer_input == input_check[-4]:
    #     last_similar_indices = []
        
    #     return Response("Input unchanged. Function disabled.")
    
    
    result = Conversation.objects.all()
    database_phrases = [conversation.chat for conversation in result]
    if len(database_phrases) == 0:
        return Response({"error": "No phrases in the database yet"}, status=status.HTTP_400_BAD_REQUEST)

    # Compute TF-IDF vectors for phrases in database and user input
    tfidf = TfidfVectorizer()
    database_vectors = tfidf.fit_transform(database_phrases)
    user_vector = tfidf.transform([customer_input])

    # Compute cosine similarities between user input and phrases in database
    similarities = cosine_similarity(user_vector, database_vectors)[0]

    # Sort the similarities in descending order and get the indices
    sorted_indices = similarities.argsort()[::-1]

    # Find the index of the next most similar phrase excluding the last remembered ones
    next_similar_index = None
    for i in sorted_indices:
        if i not in last_similar_indices:
            next_similar_index = i
            break

    if next_similar_index is None:
        # Reset the remembered indices if all similar phrases have been returned
        last_similar_indices = []

        # Get the index of the next most similar phrase
        next_similar_index = sorted_indices[0]

    # Add the current index to the list of remembered indices
    last_similar_indices.append(next_similar_index)

    # Get the most similar phrase from the database
    most_similar_phrase = database_phrases[next_similar_index]
    most_similar_phrase = most_similar_phrase.replace('Q', 'בחורה:')
    most_similar_phrase = most_similar_phrase.replace('K', 'גבר:')
    most_similar_phrase = most_similar_phrase.replace('W', 'woman:')
    most_similar_phrase = most_similar_phrase.replace('M', 'man:')

    # Split the most similar phrase into sentences based on "woman," "man," "גבר," and "בחורה"
    sentences = re.split(r'(?:woman|man|גבר|בחורה)', most_similar_phrase)

    # Compute cosine similarities between user input and sentences in the most similar phrase
    sentence_vectors = tfidf.transform(sentences)
    sentence_similarities = cosine_similarity(sentence_vectors, user_vector).flatten()

    # Find index of sentence with highest cosine similarity
    most_similar_sentence_index = sentence_similarities.argmax()

    # Get the most similar sentence from the most similar phrase
    emphasized_sentence = sentences[most_similar_sentence_index].strip()
    
    # Emphasize the most similar sentence in the most similar phrase
    emphasized_phrase = most_similar_phrase.replace(emphasized_sentence, f"<b>{emphasized_sentence}</b>")
    # print(emphasized_phrase,'empppppp')    

    if request.method == 'POST':
        query=request.data.get('query')
        print(query,'query')
        response=request.data.get('response')
        chat_room_id=request.data.get('chat_room')
        print(chat_room_id,'idddddddddd')
        if chat_room_id is None or chat_room_id == '' or chat_room_id == 'null' or chat_room_id == 'Null' or chat_room_id == 'NULL':
            username=request.data.get('username')
            user = User.objects.filter(username=username).first()
            userid=user.id
            user = User.objects.get(pk=userid)
            chat_room_id = Chatroom.objects.filter(user=user).aggregate(max_chat_room_id=Max(Cast('chat_room_id', models.IntegerField())))['max_chat_room_id']
            
            
            if chat_room_id is None or chat_room_id == '' or chat_room_id == 'null' or chat_room_id == 'Null' or chat_room_id == 'NULL':

                print(chat_room_id,'gggggggg')
                username=request.data.get('username')
                user = User.objects.filter(username=username).first()
                userid=user.id
                user = User.objects.get(pk=userid)
                save_to_chat_room=Chatroom(user=user,chat_room_id=1,response=response,query=query)
                save_to_chat_room.save()
                serializer = ConversationSerializer(data=request.data)
                if serializer.is_valid():
                    emphasized_phrase = str(emphasized_phrase)
                    return Response(emphasized_phrase, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # chat_room_id = Chatroom.objects.filter(user=user).aggregate(max_chat_room_id=Max(Cast('chat_room_id', models.IntegerField())))['max_chat_room_id']
            chat_room_id=chat_room_id+1
            save_to_chat_room=Chatroom(user=user,chat_room_id=chat_room_id,response=response,query=query)
            save_to_chat_room.save()
            serializer = ConversationSerializer(data=request.data)
            if serializer.is_valid():
                emphasized_phrase = str(emphasized_phrase)
                return Response(emphasized_phrase, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username=request.data.get('username')
        user = User.objects.filter(username=username).first()
        
        userid=user.id
        user = User.objects.get(pk=userid)
        save_to_chat_room=Chatroom(user=user,chat_room_id=chat_room_id,response=response,query=query)
        save_to_chat_room.save()
        serializer = ConversationSerializer(data=request.data)
        print(query,'query')
        print(response,'response')
        print( chat_room_id,' chat_room_id')
        print( userid,' userid')
        if serializer.is_valid():
            emphasized_phrase = str(emphasized_phrase)
            
            return Response(emphasized_phrase, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
import json

from django.db import models
from django.db.models import Max
from django.db.models.functions import Cast
@api_view(['GET'])
def get_max_room_id(request):
    username = request.GET.get('username', None)
    print(username,'lalalala')
    if username is not None:
        user = User.objects.filter(username=username).first()
        if user:
            new_chatroom_number = Chatroom.objects.filter(user=user).aggregate(max_chat_room_id=Max(Cast('chat_room_id', models.IntegerField())))['max_chat_room_id']
            print(new_chatroom_number,'newchatrom')
            # check if new_chatroom_number is None, if it is, it means that the user doesn't have any chatroom yet
            if new_chatroom_number is None:
                new_chatroom_number = 0
            # else:
            #     new_chatroom_number += 1  # increment to the next available id

            return Response({'max_chat_room_id': new_chatroom_number}, status=status.HTTP_200_OK)
    return Response({"error": "Username not provided or user does not exist"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def newchatroom(request):
    
    
    if request.method == "POST":
        data = json.loads(request.body)
        user = data.get('user')
        user = User.objects.filter(username=user).first()
        user=user.id
        chatroom = data.get('chatroom')
        print(user,'userim')
        print(chatroom,'chatim')
        if chatroom is None or chatroom == '' or chatroom == 'null' or chatroom == 'Null' or chatroom == 'NULL':
                
                new_chatroom_number = Chatroom.objects.filter(user=user).aggregate(max_chat_room_id=Max(models.functions.Cast('chat_room_id', models.IntegerField())))['max_chat_room_id']
                print(new_chatroom_number,'fffffff')
                if new_chatroom_number == None or new_chatroom_number == '': #if its a new user without chat rooms
                    new_chatroom_number = 0
                    new_chatroom_number = int(new_chatroom_number) + 1
                    print(new_chatroom_number,'newchaaaa')
                    return Response(new_chatroom_number, status=status.HTTP_201_CREATED)
                else:
                    print(type(new_chatroom_number),'beforeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                    temp = int(new_chatroom_number) + 1
                    
                    print(temp,'newchaaaa1')
                    print(type(temp),'typey')
                  
                    return Response(temp, status=status.HTTP_201_CREATED)
        return Response(chatroom, status=status.HTTP_201_CREATED)
    ################################################################### code for search openers:
@api_view(['POST'])
def searchopeners(request):
    result = Openers.objects.all()
    database_phrases = [conversation.opener for conversation in result]

    # Find a random index
    random_index = random.randint(0, len(database_phrases) - 1)

    # Get a random phrase from the database
    random_phrase = database_phrases[random_index]

    if request.method == 'POST':
        serializer = OpenersSerializer(data=request.data)
        
        if serializer.is_valid():
            emphasized_phrase = str(random_phrase)
            
            return Response(emphasized_phrase, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#########################################################################################
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match'})

        try:
            user = User.objects.create_user(email=email, username=username, password=password)
            print(user)

            return JsonResponse({'success': 'User created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request method'})


from django.http import JsonResponse
@api_view(['GET', 'POST'])
def cart_list(request):
    
   
    if request.method == 'GET':
        user_name = request.query_params.get('user')
        
        user = User.objects.filter(username=user_name).first()
        
        if user:
            carts = Cart_new.objects.filter(user=user)
            serializer = CartSerializer(carts, many=True)
            return Response(serializer.data)

    
    elif request.method == 'POST':
        # Questions.objects.all().delete()
        user_name = request.data['user_name']
        user = User.objects.filter(username=user_name).first()
        chat_value = request.data['chat']
        communitytext = request.data['communitytext']
        print(communitytext,'communitytext')
       
        
       
        cleaned_chat_value = chat_value.replace('<b>', '').replace('</b>', '')
        cleaned_chat_value = re.sub(r'\bman\b', 'M', cleaned_chat_value)  # Replace "man:" with "M"
        cleaned_chat_value = re.sub(r'\bwoman\b', 'W', cleaned_chat_value)  # Replace "woman" with "M"
        cleaned_chat_value=cleaned_chat_value.replace(':',"")

        
   
        try:
            cleaned_chat_value = cleaned_chat_value.replace('גבר', 'K').replace('בחורה', 'Q')  # Replace "man" with "M" and "woman" with "W"
            
        except:
            print ('not found')
       
        print(cleaned_chat_value,'the value of the phrase')
        # Create a Conversation object with the chat value
        chat = Conversation.objects.filter(chat=cleaned_chat_value).first()
        if chat is None:
            chat = Answer.objects.filter(users_answer=cleaned_chat_value).first()
            if chat is None:
                return Response({"error": "Chat not found"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create a new Conversation with the Answer's users_answer
                conversation = Conversation.objects.create(chat='Q'+communitytext+'K'+chat.users_answer)
              
                serializer = CartSerializertwo(data={'user': user.id, 'chat': conversation.id})
        else:
            serializer = CartSerializertwo(data={'user': user.id, 'chat': chat.id})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from django.http import JsonResponse
@api_view(['GET', 'POST'])
def cart_list_openers(request):
    
   
    if request.method == 'GET':
        user_name = request.query_params.get('user')
        
        user = User.objects.filter(username=user_name).first()
        
        if user:
            carts = Cart_openers.objects.filter(user=user)
            serializer = OpenersSerializer(carts, many=True)
            return Response(serializer.data)

    from django.core.exceptions import ObjectDoesNotExist

#...

    if request.method == 'POST':
        user_name = request.data['user_name']
        user = User.objects.filter(username=user_name).first()
        chat_value = request.data['chat']

        cleaned_chat_value = chat_value.replace('<b>', '').replace('</b>', '')
        cleaned_chat_value = re.sub(r'\bman\b', 'M', cleaned_chat_value)  # Replace "man:" with "M"
        cleaned_chat_value = re.sub(r'\bwoman\b', 'W', cleaned_chat_value)  # Replace "woman" with "W"
        cleaned_chat_value=cleaned_chat_value.replace(':',"")

        try:
            cleaned_chat_value = cleaned_chat_value.replace('גבר', 'K').replace('בחורה', 'Q')  # Replace "man" with "M" and "woman" with "W"
        except:
            print ('not found')

        print(cleaned_chat_value,'the value of the phrase')

        try:
            chat = Openers.objects.get(opener=cleaned_chat_value)
        except ObjectDoesNotExist:
            return Response({'error': 'No opener found with this value.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OpenersSerializer(data={'user': user.id, 'opener': chat.id})

        if serializer.is_valid():
            # serializer.save()

            # Create a Cart_openers object with the chat value after serializer is valid and saved
            Cart_openers.objects.create(user=user, opener=chat)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







@api_view(['DELETE'])
def deletetfromcart_openers(request, pk, username):
    # Get the Cart_openers object using the pk
    cart_item = Cart_openers.objects.get(id=pk)
    # Openers.objects.all().delete()
    
    # Verify that the cart item belongs to the user
    if cart_item.user.username != username:
        return Response({"error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Delete the Cart_openers object
    cart_item.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def deletetfromcart(request,pk,username):
    print(pk,'kkkkkkk')

    if request.method == 'DELETE':
        user_name = username
        user = User.objects.filter(username=user_name).first()
        userid=user.id
        print(userid,'userrrrr')

        # Try getting the specific cart item to delete
        try:
            deletedprod = Cart_new.objects.filter(chat_id=pk, user_id=userid)
        except Cart_new.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        print(deletedprod,'hhhhhhhhhhhhhhhhhhhhhhhh')

        # Delete the specific cart item
        deletedprod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    

@api_view(['GET','DELETE'])
def chat_room(request):
    # if request.method == 'DELETE':
    #     # data = json.loads(request.body)
    #     user = request.data.get('user')
    #     user = User.objects.filter(username=user).first()
    #     chatroom_number=Chatroom.objects.filter(user=user)
       
    #     # chatroom_number=
    #     print(chatroom_number,'hhhttt122222222222222222222222222222222222222222222222222222222222')
    #     return Response('hhh', status=status.HTTP_201_CREATED)

    
    if request.method == 'GET':
        user_name = request.query_params.get('user')
        
        user = User.objects.filter(username=user_name).first()
        print(user.id,'dfdd555')
        if user:
            specific_chatroom_phrases = Chatroom.objects.filter(user=user)
            print(specific_chatroom_phrases,'fff')
            serializer = ChatroomSerializer(specific_chatroom_phrases, many=True)
            return Response(serializer.data)



@api_view(['GET'])
def chat_history(request):
    chat_room_id = request.query_params.get('chat_room_id')
    username = request.query_params.get('user')
    user = User.objects.filter(username=username).first()
    if user:
        chat_history = Chatroom.objects.filter(user=user, chat_room_id=chat_room_id)
        print(chat_history,'history')
        serializer = ChatroomSerializer(chat_history, many=True)
        return Response(serializer.data)
    else:
        return Response({"detail": "User not found"}, status=404)
    
@api_view(['POST'])
def insert_question(request):
    if request.method == 'POST':
        username=request.data.get('username')
        question=request.data.get('question')
        print(username,'q-username')
        print(question,'q-question')
    
        try:
            user = User.objects.filter(username=username).first()
            generate_question = Questions.objects.create(user=user, users_question=question)
           
            # generate_question=str(generate_question)
            print(generate_question.users_question_id,'generated')
            serializer = QuestionsSerializer(generate_question)
            return Response(serializer.data)
          
        except User.DoesNotExist:
            return None
        

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def extract_question(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        print(username,'q-username')

        try:
            user = User.objects.get(username=username)
            extract_question = Questions.objects.filter(is_answered=0).exclude(user=user).order_by('created_at').first()

            if extract_question is not None:
                print(extract_question,'hhhhhhhhhhhhhhh')
                serializer = QuestionsSerializer(extract_question)
                return Response(serializer.data)
            else:
                return Response({"error": "No unanswered questions available from other users."})

        except User.DoesNotExist:
            return Response({"error": "User does not exist."})



@api_view(['POST'])
def insert_answer(request):
    if request.method =='POST':
        users_question_id=request.data.get('users_question_id')
        answer=request.data.get('answer')
        print(users_question_id,'q-id')
        print(answer,'answer')
        Answer.objects.create(questions_id=users_question_id, users_answer=answer)
        questiones_id=Answer.objects.filter(questions_id=users_question_id)
        count = questiones_id.count()
        print(count,'count')
        if count >= 2:
            relevant_questions =Questions.objects.filter(users_question_id=users_question_id)
            for i in relevant_questions:
                print(i.is_answered,'before')
                i.is_answered=True
                print(i.is_answered,'after')
                i.save()

                return Response('answered and not reachable')
        else:
        
            return Response('sssucesss')
        

from rest_framework.exceptions import NotFound

@api_view(['GET'])
def extract_answer(request):
    if request.method == 'GET':
        print (request.data,'dataaaaaaaaaaaaaaaaaaa')

        users_question_id=request.GET.get('users_question_id')
        username=request.GET.get('username')
        print(users_question_id,'ieeeee4')
        print(username,'username for extract answer')
        user2 = User.objects.get(username=username)
        print (user2,user2.id,'user222222222222222222')
        user2_id=user2.id
        if users_question_id=='':
            relevant_question1 = Questions.objects.filter(user_id=user2_id).order_by('users_question_id').last()
            print(relevant_question1,'new one')
            # new_filter_for_answer=Answer.objects.filter(questions_id=relevant_question1).values('users_answer')
            if relevant_question1 == None:
                return Response('Sorry-none')
            new_filter_for_answer=Answer.objects.filter(questions_id=relevant_question1.users_question_id)
            

            print(new_filter_for_answer,'new_filter_for_answer')
            serializer = AnswersSerializer(new_filter_for_answer, many=True)
            return Response(serializer.data)  # Change from request.data to request.GET
        else:
            return Response('Sorry')
        # try:    
            # user = User.objects.get(username=username)
            # print(user.id,'usrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
            # user=user.id
        # relevant_question = Questions.objects.filter(users_question_id=users_question_id).values('user_id', 'users_question_id')
        # for question in relevant_question:
        #     user_id = question['user_id']
        #     users_question_id = question['users_question_id']
        #     print(f"User ID: {user_id}, Users Question ID: {users_question_id}")

        #     # Compare user_id with user2
        # print (user2_id,"user2 new IDDDDDDDD")
        # if user_id == user2_id:
        #     print("user2 and the user_id from the queryset are the same.")
        # else:
        #     print("user2 and the user_id from the queryset are different.")
        #     print('@@@@@@@@@@@@@@@@@@@@@@@@')

        # print(relevant_question,'usersID_that asked the question')
        # if relevant_question.is_answered == True :
        #     print(relevant_question,'is true')
        #     answers = relevant_question.answers.all()
        #     print(answers,'answerssss')  # Get associated answers
        #     serializer = AnswersSerializer(answers, many=True)
        #     return Response(serializer.data)
        # else: 
        #     return Response('notyet')

        # except Questions.DoesNotExist:
        #     raise NotFound('Question with id {} does not exist.'.format(users_question_id))

                
            # else:
            #     return Response('not true')
@method_decorator(csrf_exempt, name='dispatch')
class DeleteChatRoomView(View):
    def delete(self, request, *args, **kwargs):
        room_id = kwargs['roomId']
        username = self.request.GET.get('username', '')

        user = User.objects.filter(username=username).first()

        # Fetch the room by id
        try:
            chat_room = Chatroom.objects.filter(user=user,chat_room_id=room_id)
        except Chatroom.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)

        # Delete the room
        chat_room.delete()

        # Respond with a success status
        return JsonResponse({"message": "Room deleted successfully"}, status=200)
    

