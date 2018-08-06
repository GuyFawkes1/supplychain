from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.views import View
import json

from .product_type import create_product_type, delete_product_type, create_role, delete_role, create_check, delete_check
from .forms import ProductTypeForm, UserForm

def random_server():
    urls_list = {'1': 'http://127.0.0.1:8008', '2': 'http://rest-api-0:8008'}
    return urls_list['2']

def index(request):
    if request.user.is_authenticated == False:
        return redirect('items:index')

    context = {'username' : request.user.username} 
    return render(request, 'ptypes/index.html', context)

def details(request):
    None
    

class CreatePageView(View) :
    product_form = ProductTypeForm
    template_name = 'ptypes/create.html'

    def get(self, request):
        if request.user.is_authenticated == False:
            return redirect('items:login')

        form = self.product_form(None)
        return render(request, self.template_name, {'form' : form})

    def post(self, request):
        if request.user.is_authenticated == False:
            return redirect('items:login')
        url = random_server()
        adminname = request.user.username
        dept = request.user.dept

        # form = ProductTypeForm(request.POST)

        ptype_name = request.POST['ptype_name']
        role_assign = request.POST['role_assign']
        check_assign = request.POST['check_assign']

        
        if role_assign is None: 
            create_product_type.create_ptype(ptype_name, dept, adminname, url)
        elif role_assign is not None and check_assign is None:
            create_role.create_role(ptype_name, dept, role_assign, None, adminname, url)
        elif role_assign is not None and check_assign is not None:
            create_check.create_check(ptype_name, dept, role_assign, check_assign, adminname, url)

class LoginView(View):
    form_class = UserForm
    template_name = 'ptypes/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('ptypes:index')

        return render(request, self.template_name, {'form':form})
 
        
