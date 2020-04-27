from django.shortcuts import render,redirect
from django.http import Http404
from django.contrib.auth import authenticate, login , logout
from django.views import View
import json
from .wallet import create as create_wal
from .wallet import finder,profile,role_defs
from .forms import CreateProfileForm
from .models import Pair


###WORK on this postponed
def random_server():
	urls_list = { '1': 'http://127.0.0.1:8008','2': 'http://rest-api-0:8008' }
	return urls_list['2']


def index(request):
	
	if request.user.is_staff == False :
		return redirect('items:index')
	#Add group permission instead of just authentication

	url = random_server()
	resp ={}
	response = finder.query_all(url)
	for s in response:
		name,pubkey,prof = response[s].decode().split(",")
		resp[name] = Pair(name,pubkey,prof)

		

	context = {'resp' :resp, 'username' : request.user.username}

	return render(request,'profiles/index.html', context)

def detail(request,username):
	
	if request.user.is_staff == False :
		return redirect('items:index')
	url = random_server()

	hist= finder.user_history(username,url)

	context = {'hist' : hist }
	return render(request,'profiles/detail.html',context)	




class CreateProfileView(View):

	form_class = CreateProfileForm
	template_name = 'profiles/create.html'

	def get(self,request):

		if request.user.is_staff == False :
			return redirect('items:login')

		form = self.form_class(None)
		return render(request,self.template_name,{'form' : form})


	def post(self,request):
		
		if request.user.is_staff == False :
			return redirect('items:login')
		url = random_server()
		form = CreateProfileForm(request.POST)
		
		if form.is_valid():
			user = form.save(commit=False)
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			
			user.set_password(password)
			user.save()
			create_wal.add(username,request.user.username,url)
			df_profs = role_defs.role_prof(username)
			profile.prof(username,df_profs,request.user.username,url)

			return redirect('profiles:home')
		else:
			return redirect('profiles:create')


	
		

