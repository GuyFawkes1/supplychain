import os
from .wal_client import WalClient
import subprocess

def _get_keyfile(name):
	username = name
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

def add(name,adminname):
	url = 'http://127.0.0.1:8008'
	res = subprocess.check_call(['sawtooth','keygen',name])

	keyfile_u = _get_keyfile(name)
	keyfile_admin = _get_keyfile(adminname)
	admin_client = WalClient(base_url=url,keyfile=keyfile_admin)
	client = WalClient(base_url=url,keyfile = keyfile_u)

	response = admin_client.create(name=name,pubkey=client._signer.get_public_key().as_hex())

	print("response: {}".format(response))

