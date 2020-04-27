#This file creates a user with username ritwick into the blockchain

import os
from wal_client import WalClient
import subprocess

def _get_keyfile(name):
	username = name
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

def add(name,adminname,url):
	# url = 'http://127.0.0.1:8008'
	try:
		res = subprocess.check_call(['sawtooth','keygen',name])
	except:
		pass

	keyfile_u = _get_keyfile(name)
	keyfile_admin = _get_keyfile(adminname)
	admin_client = WalClient(base_url=url,keyfile=keyfile_admin)
	client = WalClient(base_url=url,keyfile = keyfile_u)

	response = admin_client.create(name=name,pubkey=client._signer.get_public_key().as_hex())

	print("response: {}".format(response))

add('ritwick','ubuntu','http://rest-api-0:8008')