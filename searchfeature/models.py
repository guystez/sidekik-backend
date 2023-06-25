# Create your models here.
from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Chatroom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False) 
    chat_room_id = models.IntegerField(null=True)
    query=models.TextField(null=True)
    response=models.TextField(null=True)


class Questions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False) 
    users_question = models.TextField(null=True)
    users_question_id = models.AutoField(primary_key=True)
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='answers')
    users_answer = models.TextField(null=True)
    users_answer_id = models.AutoField(primary_key=True)
    
    

class Conversation(models.Model):
    chat = models.TextField(null=True)
    
    def get_chat(self):
        return self.chat
    

class Openers(models.Model):
    opener = models.TextField(null=True)
    
    def __str__(self):
        return self.opener



class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    stripe_charge_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    timelap = models.TextField(null=True)


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# class User(AbstractBaseUser):
#     email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
#     username = models.CharField(max_length=30, unique=True)
#     first_name = models.CharField(max_length=30, blank=True)
#     last_name = models.CharField(max_length=30, blank=True)
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)

#     objects = MyUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self): 
        return self.is_admin

class Cart_new(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    chat = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True )

    def __str__(self):
        return f"User: {self.user.id}, Chat: {self.chat.id}"

    

class Cart_openers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    opener = models.ForeignKey(Openers, on_delete=models.CASCADE, null=True )

    def __str__(self):
        return self.name


