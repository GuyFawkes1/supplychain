from django.shortcuts import render,get_object_
from .sawtooth import querying
from django.http import Http404

# Create your views here.

def index(request):
	response = querying.query_all_items()
	return render(request,'items/index.html',response)
'''
def detail(request,itemname):
	try:
		response = finder.find(itemname,'ubuntu')
	except:
		raise Http404("Item Doesn't exist")
		
	return render(request,'items/detail.html',response)	
'''