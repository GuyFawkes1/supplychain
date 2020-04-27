import os
from wal_client import WalClient

def _get_keyfile():
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

def prof(name,profile):
	url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile()
	client = WalClient(base_url=url,keyfile = keyfile)

	response = client.prof(name=name,profile = profile)

	print("response: {}".format(response))

