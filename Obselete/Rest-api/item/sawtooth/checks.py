import os
from hw_client import HwClient

def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

#different check functions will be called for different checks

def check1(name,cu_add,usrname):
	url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile(usrname)
	client = HwClient(base_url=url,keyfile = keyfile)

	response = client.check(name=name,check_no='check1',cu_add=cu_add)

	print("response: {}".format(response))

def check2(name,cu_add,usrname):
	url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile(usrname)
	client = HwClient(base_url=url,keyfile = keyfile)

	response = client.check(name=name,check_no='check2',cu_add=cu_add)

	print("response: {}".format(response))

def check3(name,cu_add,usrname):
	url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile()
	client = HwClient(base_url=url,keyfile = keyfile)

	response = client.check(name=name,check_no='check3',cu_add=cu_add)

	print("response: {}".format(response))

def check4(name,cu_add,usrname):
	url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile()
	client = HwClient(base_url=url,keyfile = keyfile)

	response = client.check(name=name,check_no='check4',cu_add=cu_add)

	print("response: {}".format(response))