import os
from .hw_client import HwClient
import requests
import hashlib
import json
import base64
from base64 import b64encode
from ..models import history_object



def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")
	return '{}/{}.priv'.format(key_dir, username)


#This is just request that is sent to the rest api running

HW_NAMESPACE = hashlib.sha512('hw'.encode("utf-8")).hexdigest()[0:6]


def make_item_address(name):
	return HW_NAMESPACE + \
		hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]



def item_history(name,url):
	#url = 'http://127.0.0.1:8008/transactions'
	url = url + '/transactions'
	
	r = requests.get(url=url)
	
	alltrans = r.json()
	address = make_item_address(name)
	j = 0
	
	history_collection = {}
	for i in alltrans['data']:
		if i['header']['outputs'] == [address]:
			#jsan[j] = (base64.b64decode(i['payload']))
			
			unprocessed = base64.b64decode(i['payload'])
			name,action,c_add,prev_add,timestamp = unprocessed.decode().split(",")
			hist = history_object(name,action,c_add,prev_add,timestamp)
			history_collection[j] = hist
			j = j+1
	return history_collection



