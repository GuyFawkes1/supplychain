import os
from wal_client import WalClient

def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

def query(name,usrname):
	#url has to be changed
	url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile(usrname)
	client = WalClient(base_url=url,keyfile = keyfile)

	response = client.show(name=name)

	print("response: {}".format(response))

