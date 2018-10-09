from django.conf.urls import url
from django.urls import path
from . import views

app_name='items'

import time
urlpatterns = [
	
	url('home/',views.index,name='index'),
	url('login/',views.UserFormView.as_view(),name= 'login'),
	url('logout/',views.logout_view,name = 'logout'),
	url('create/',views.CreateItemView.as_view(),name='create'),
	url('map/',views.map,name='map'),
	path('details/<itemname>/',views.detail,name='detail'),
	path('details/<itemname>/checks/',views.checked , name = 'checked'),
	path('users-details/<username>/',views.user_detail,name='user_detail'),
	path('send/<itemname>/',views.send,name = 'send')

]