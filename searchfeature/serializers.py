from rest_framework import serializers
from .models import Answer, Cart_new, Chatroom, Conversation, Openers, Questions


class ChatroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatroom
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class OpenersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Openers
        fields = '__all__'




class CartSerializer(serializers.ModelSerializer):
    chat = ConversationSerializer()
    class Meta:
        model = Cart_new
        fields = '__all__'

class CartSerializertwo(serializers.ModelSerializer):
    
    # chat = ConversationSerializer()

    class Meta:
        model = Cart_new
        fields = '__all__'



