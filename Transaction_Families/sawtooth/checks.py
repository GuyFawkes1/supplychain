import os
from .hw_client import HwClient
from .finder import find

def _get_keyfile(usrname):
	username = usrname
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")

	return '{}/{}.priv'.format(key_dir, username)

#different check functions will be called for different checks

def check(name,cu_add,checkno,usrname,url):
	# url = 'http://127.0.0.1:8008'
	keyfile = _get_keyfile(usrname)
	client = HwClient(base_url=url,keyfile = keyfile)
	finding_item = find(name,usrname,url)
	# print("printing c_addr")
	# print(finding_item[name].c_addr)
	# print("printing signerkeyas hex")
	# print(client._signer.get_public_key().as_hex())
	finding_item[name].c_addr == client._signer.get_public_key().as_hex()
	response = client.check(name=name,check_no=checkno,cu_add=usrname)
	#only when the transaction is not pending it will return control back to django
	return response


def item_checks_list(check_status,profile):
	checks = {}
	
	checks[1]= "Pallet restacked at sterilizer"
	checks[2]= "PDP Product"
	checks[3]= "Ready for sterilization"
	checks[4] = "Sterilization Confirmation by Mfg"
	checks[5] = "Sterilized"
	checks[6] = "Confirmation by Coventry QA"
	checks[7] = "LAL/Endotoxin Testing"
	checks[8] = "DES Batch Release Testing"
	checks[9] = "Final Functional Testing"


	check_entire = {}
	j=0
	for i in checks:
		
		check_entire[j] = check_class(checks[i],check_status[j]== '-',profile[j]=='X')
		j = j+1

	
	return check_entire

class check_class(object):
	def __init__(self,name,check,auth):
		self.name = name
		self.check = check
		self.auth = auth