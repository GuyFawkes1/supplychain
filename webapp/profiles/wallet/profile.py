import os
from .wal_client import WalClient

def _get_keyfile(username):
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

def prof(name,profile,adminname,url):
	#url = 'http://127.0.0.1:8008'
	admin_keyfile = _get_keyfile(adminname)

	admin_client = WalClient(base_url=url,keyfile = admin_keyfile)

	response = admin_client.prof(name=name,profile = profile)

	return response


