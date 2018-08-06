from django.conf.urls import url
from django.urls import path
from . import views

app_name='ptypes'

import time
urlpatterns = [
    url('home/', views.index, name = 'index'),
    url('login/', views.LoginView.as_view(), name = 'login'),
    url('create/', views.CreatePageView.as_view(), name = 'create'),
    url('details/', views.details, name = 'details') 

]