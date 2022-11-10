from django.contrib import admin
from django.urls import path, include
from .views import *
from sign.views import *

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetail.as_view(), name='post'),
    path('add/', AddList.as_view()),
    path('personalpage/', PersonalPage.as_view()),
    path('accept/<int:pk>', AcceptReplyView.as_view(), name='reply_accept'),
    path('delete/<int:pk>', ReplyDeleteView.as_view(), name='reply_delete'),
    path('edit/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('personaloffice/<int:pk>', UserUpdateView.as_view(), name='personaloffice'),
    path('subscribers/', AddSubscribers.as_view(), name='add_subscribers'),
    path('code/<str:user>', GetCode.as_view(), name='code'),
    path('set_password/<str:user>', SetPassword.as_view(), name='password'),

]