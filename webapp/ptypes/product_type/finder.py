# This file finds the state of an item
import os
from .ptype_client import PtypeClient

def _get_keyfile(adminame):
	home = os.path.expanduser("~")
	key_dir = os.path.join(home, ".sawtooth", "keys")
	return '{}/{}.priv'.format(key_dir, adminame)

def find(name,usrname,url):
	keyfile = _get_keyfile(usrname)
	ptype_client = PtypeClient(base_url = url, keyfile = keyfile)
	response = ptype_client.show(name = name)
	response = _deserialize(response)
	return response

class Ptype(object):
	def __init__(self, ptype_name, dept, role):
		self.name = ptype_name
		self.dept = dept
		self.role = role

def _deserialize(data):
		ptypes = {}
		try:
			for ptype in data.decode().split("|"):
				name, dept, role = ptype.split(",")
				ptypes[name] = Ptype(name, dept, role)

		except ValueError:
			pass
			
		return ptypes
