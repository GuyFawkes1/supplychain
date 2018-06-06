# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .wallet import create
from .wallet import delete

from .wallet import finder
from .wallet import profile

#add serialllization stuff here only


#item_1/
#check if there exists a keyfile --- probably should go into wallet_tf
#handle authentications somewhere!!!!!!!!!
#error handling when keyfile is non existent

class profile_create(APIView):
		
	def post(self,request):
		json_req = json.loads(request.body.decode())
		response = create.add(json_req["new_name"])
		return Response("Creation of profile initated")



class profile_delete(APIView):
	def post(self,request):
		json_req = json.loads(request.body.decode())
		response = delete.delete(json_req["username"])
		return Response("Item deletion Initiated")


class key_finder(APIView):
	def get(self,request):
		json_req = json.loads(request.body.decode())

class profile_edit(APIView):
	def post(self,request):
		json_req = json.loads(request.body.decode())
		response = profile.prof(json_req["username"], json_req["new_profile"])

