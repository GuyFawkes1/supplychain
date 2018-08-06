# In the entire item state database if the user exists, 
# what other items are currently stored with that user
# The response is returned to views.py (line 37?)

import os
from .hw_client import HwClient
from ..models import Item
import requests
import hashlib
import json
import base64
from base64 import b64encode

HW_NAMESPACE = hashlib.sha512('hw'.encode("utf-8")).hexdigest()[0:6]


def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")
	return '{}/{}.priv'.format(key_dir, username)


def query_all_items(url):
	url = url + '/state'

	r = requests.get(url = url)
	allstates = r.json()
	
	jsan = {}
	j=0
	for i in allstates['data']:
		if i['address'][0:6]== HW_NAMESPACE:
			jsan[j] = (base64.b64decode(i['data']))
			j = j+1
	return jsan

def query_possible_items(partial_name,url):
	url = url + '/state'
	r = requests.get(url= url)
	allstates = r.json()
	item_dict = {}
	j = 0
	for i in allstates['data']:
		if i['address'][0:6] == HW_NAMESPACE:
			serialized = (base64.b64decode(i['data']))
			name,checks,c_add,prev_add = serialized.decode().split(",")
			if partial_name in name:
				item = Item(name,checks,c_add,prev_add)
				item_dict[name] = item
				j = j+1

	return item_dict



def query_user_held(usrname,url):
	url = url + '/state'
	keyfile = _get_keyfile(usrname)
	client = HwClient(base_url=url,keyfile = keyfile)
	public_key = client._signer.get_public_key().as_hex()
	
	r = requests.get(url = url)
	allstates = r.json()

	item_dict = {}
	j = 0
	for i in allstates['data']:
		if i['address'][0:6] == HW_NAMESPACE:
			serialized = (base64.b64decode(i['data']))
			name,checks,c_add,prev_add = serialized.decode().split(",")
			if c_add == public_key :
				item = Item(name,checks,c_add,prev_add)
				item_dict[name] = item
				j = j+1

	return item_dict