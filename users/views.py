import webbrowser
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import serializers

from searchfeature.register import NewUserForm
from . import serializers
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from searchfeature.serializers import ConversationSerializer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.contrib.auth import login
from django.contrib.messages import error, success
from django.views.decorators.csrf import ensure_csrf_cookie
from . import serializers
from users.serializers import LoginSerializer

import users

class LoginView(views.APIView):
  
   permission_classes = (permissions.AllowAny,)

    
   def post(self, request, format=None):
       serializer = LoginSerializer(data=self.request.data,context={ 'request': self.request })
    
       serializer.is_valid(raise_exception=True)
       user = serializer.validated_data['user']
       password = serializer.validated_data['password']
       print(user)
       print(password)
       login(request, user,password)
       return Response(None, status=status.HTTP_202_ACCEPTED)



class LogoutView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, format=None):
        logout(request)
        response = Response(None, status=status.HTTP_204_NO_CONTENT)
        response.set_cookie('sessionid',max_age=1,samesite='None')
        response.set_cookie('csrftoken',max_age=1,samesite='None')
        return response

class ProfileView(generics.RetrieveAPIView):
    serializer_class = serializers.LoginSerializer

    def get_object(self):
        return self.request.user
    





from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.response import Response
from searchfeature.register import NewUserForm
from users.serializers import serializers ,RegisterSerializer
from django.contrib.auth.models import User
import requests
import json


#  url = 'https://www.google.com'
#             site = webbrowser.open(url)
#             if site != False:
#                 print('closed')
class Get_payment(views.APIView):
    def post(self, request):

        headers = {
                    "api_key": "95ed9b8d-8702-4c54-9dd8-b9242c7e3427",
                    "api_secret": "488447db-0503-4fc8-9ed0-4e1d62ee0114"
                }

        data = {
            
            "order_reference": "YOUR_ORDER_REFERENCE",
            "redirectAddress": "YOUR_REDIRECT_ADDRESS",
            "recurringDue_date": "YOUR_RECURRING_DUE_DATE",
            "recurringInterval": "3",
            "interval": "5",
            "dealType": "4",
            "createDocument": "True",
            "DisplayType": "iframe",
			"PostProcessMethod": 0,
            'RedirectAddress':"http://localhost:3000/thankyoupage/"
        }
       

        response = requests.post('https://api.takbull.co.il/api/ExtranalAPI/GetTakbullPaymentPageRedirectUrl', headers=headers, json=data)
        if response.status_code == requests.codes.ok:
            print(response.content,'llllllllllllllllllllllllllllll')
            print("Accept headers: ", response.json())
            answer= response.json()
            

            return Response(answer)

        else:
            print("Request failed with status code: ", response.status_code)
    
  
   

class RegisterView(views.APIView):
    def post(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                serializer.validated_data['username'],
                serializer.validated_data['email'],
                serializer.validated_data['password'],
                
            )
           

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)