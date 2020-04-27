import os
from .hw_client import HwClient
import requests
import hashlib
import json
import base64
from base64 import b64encode



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



def item_history(name):
	url = 'http://127.0.0.1:8008/transactions'
	
	r = requests.get(url=url)
	alltrans = r.json()
	address = make_item_address(name)
	j = 0
	jsan = {}
	for i in alltrans['data']:
		if i['header']['outputs'] == [address]:
			jsan[j] = (base64.b64decode(i['payload']))
			j = j+1
	return jsan

def user_history(usrname):
	keyfile = _get_keyfile(usrname)
	url =  'http://127.0.0.1:8008/transactions'
	client = HwClient(base_url=url,keyfile = keyfile)
	public_key = client._signer.get_public_key().as_hex()
	r = requests.get(url=url)
	alltrans = r.json()
	jsan = {}
	j=0
	for i in alltrans['data']:
		if i['header']['signer_public_key'] == public_key:
			jsan[j] = (base64.b64decode(i['payload']))
			j = j+1
	
	return jsan


