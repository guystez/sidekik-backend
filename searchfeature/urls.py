from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static 
from .views import create_user
from .views import DeleteChatRoomView

app_name = 'searchfeature'

urlpatterns = [
path("create_new_room/", views.newchatroom, name= "newchatroom"),
path("search/", views.search, name= "search"),
path("cart/", views.cart_list, name= "cart_list"),
path("cart_openers/", views.cart_list_openers, name= "cart_list"),
path("chat_room/", views.chat_room, name= "chat_room"),
path("searchopeners/", views.searchopeners, name= "search"),
path("insert_db/", views.insert_db, name= "insert_db"),
path("insert_db_openers/", views.insert_db_openers, name= "insert_db_openers"),
path('signup/', create_user, name='create_user'),
path('chat_history/', views.chat_history, name='chat_history'),
path('generate_question/', views.insert_question, name='insert_question'),
path('extract_question/', views.extract_question, name='extract_question'),
path('extract_answer/', views.extract_answer, name='extract_answer'),
path('insert_answer/', views.insert_answer, name='insert_answer'),
path('delete_room/<int:roomId>/', DeleteChatRoomView.as_view(), name='delete-room'),   
path('get_max_room_id/', views.get_max_room_id, name='get_max_room_id'),
path("deletecart/<pk>/<username>", views.deletetfromcart, name= "deletefromcart"),
path("deletecart_openers/<pk>/<username>", views.deletetfromcart_openers, name= "deletefromcart"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


