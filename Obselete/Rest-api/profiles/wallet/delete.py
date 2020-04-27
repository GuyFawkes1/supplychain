import os
from .wal_client import WalClient

def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)



#delete is gonna dance
#check for admin previlages
def delete(u_name,adminname):
	url = 'http://127.0.0.1:8008'
	keyfile_u = _get_keyfile(u_name)
	keyfile_a = _get_keyfile(adminname)
	client = WalClient(base_url=url,keyfile = keyfile_u)
	admin_client = _get_keyfile(adminname)
	response = admin_client.delete(name=u_name,pubkey = client._signer.get_public_key().as_hex())

	print("response: {}".format(response))
