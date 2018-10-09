import os
from .wal_client import WalClient
import requests
import hashlib
import json
import base64
from base64 import b64encode
from ..models import history_object
WAL_NAMESPACE = hashlib.sha512('wal'.encode("utf-8")).hexdigest()[0:6]

def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

def query(name,usrname,url):
	#url has to be changed
	# url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile(usrname)
	client = WalClient(base_url=url,keyfile = keyfile)
	response = client.show(name=name)
	return response

def query_all(url):
	url = url + '/state'

	r = requests.get(url = url)
	allstates = r.json()
	
	jsan = {}
	j=0
	for i in allstates['data']:
		if i['address'][0:6]== WAL_NAMESPACE:
			jsan[j] = (base64.b64decode(i['data']))
			j = j+1
	return jsan

def user_history(usrname,url):
	keyfile = _get_keyfile(usrname)
	url =  url + '/transactions'
	client = WalClient(base_url=url,keyfile = keyfile)
	public_key = client._signer.get_public_key().as_hex()
	r = requests.get(url=url)
	alltrans = r.json()
	jsan = {}
	j=0
	history_collection = {}
	for i in alltrans['data']:
		if i['header']['signer_public_key'] == public_key :
			unprocessed = base64.b64decode(i['payload'])
			try:
				name,action,c_add,prev_add,timestamp = unprocessed.decode().split(",")
				hist = history_object(name,action,c_add,prev_add,timestamp)
			except:
				name,action,pubkey = unprocessed.decode().split(",")
				hist = history_object(None,action,name,None,pubkey)
				print("ALl OKAY")
			history_collection[j] = hist
			j = j+1
		
	return history_collection


