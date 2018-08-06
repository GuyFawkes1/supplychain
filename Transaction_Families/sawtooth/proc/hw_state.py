import hashlib

from sawtooth_sdk.processor.exceptions import InternalError

# 128-digit hexadecimal number for the first 6 digits of each transaction family is created
# The first 6 digits from the number is extracted
# This will correspond to the transaction family in the state adresss
HW_NAMESPACE = hashlib.sha512('hw'.encode("utf-8")).hexdigest()[0:6]

WAL_NAMESPACE = hashlib.sha512('wal'.encode("utf-8")).hexdigest()[0:6]


# Complete state address is created 
# Using the 6 digits corresponding to transaction family 
# And first 64 digits from the hexadecimal number for the item or user name
def _make_wal_address(name):
	return WAL_NAMESPACE + \
		hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

def _make_hw_address(name):
	return HW_NAMESPACE + \
		hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

# Item object that includes the item name, checks that have been completed 
# the current users address and the previous users address
# Individual state data stored in the items's state database is created via this object
class Item(object):
	def __init__(self,name,check,c_addr,p_addr):
		self.name = name
		self.check = check
		self.c_addr = c_addr
		self.p_addr = p_addr

# User object that includes their name, profile (checks that can be completed by them)
# and their public key
# Individual state data stored in the user's state database is created via this object
class Pair(object):
	def __init__(self,name,pubkey,prof, role):
		self.name = name
		self.prof = prof
		self.pubkey = pubkey
		self.role = role


# Object parameter receives individual state data
# Either adds new state data with a new state address to the state database
# Or replaces existing state data at the state address with the most current data
# Actions denoted by transactions are implemented here
class HwState(object):
	
	TIMEOUT = 3
	# context is given - current state relevant to the transaction processor 
	# if you change anything to context it will eventually be changed in the main state
	def __init__(self,context):
		self._context = context
		self._address_cache = {}
		# addresses you have seen in this iteration of the script

	# Deletes the instance of the item from the dictionary of state addresses to state data
	def delete_item(self,item_name):
		# Dictionary where keys are the state address and the value is the state data
		items = self._load_items(item_name = item_name)

		# There may be an exception where one address stores data for more than one item
		# If this is the case, the dictionary of state addressses and remaining state data is restored
		# Else the state address and state data is deleted
		del items[item_name]
		if items:
			self._store_item(item_name,items = items)
		else:
			self._delete_item(item_name)

	# Retrieves the public key for the user 
	# This method is primarily used in hw_transhand
	def get_pubkey(self,name):
		key_address = _make_wal_address(name)
		key_state_entry = self._context.get_state([key_address],timeout=self.TIMEOUT)
		
		if key_state_entry :
			pubkey = self._deserialize_key(data=key_state_entry[0].data)
			return pubkey[name].pubkey
		else:
			print("Reciever doesn't exist in the database")
			return None

	# Retrieves the profile of the user 
	# Profile pertains to the checks a user is authorized to conduct
	def get_prof(self,name):
		key_address = _make_wal_address(name)
		key_state_entry=self._context.get_state([key_address],timeout=self.TIMEOUT)
		
		if key_state_entry :
			pubkey = self._deserialize_key(data=key_state_entry[0].data)
			return pubkey[name].prof

		else:

			print("Reciever doesn't exist in the database")
			return None

	# Sets the item to its corresponding state address
	def set_item(self,item_name,item):
		items = self._load_items(item_name= item_name)

		items[item_name] = item

		self._store_item(item_name,items = items)

	# Retrieves the individual state data from the state database
	def get_item(self,item_name):
		return self._load_items(item_name=item_name).get(item_name)

	# Serializes state data and stores the data with its corresponding
	# state address in the state database
	def _store_item(self,item_name,items):

		address = _make_hw_address(item_name)

		state_data = self._serialize(items)

		self._address_cache[address] = state_data
		self._context.set_state({address: state_data},timeout=self.TIMEOUT)

	# Deletes state data for an item and its state address from the state database
	def _delete_item(self,item_name):
		address = _make_hw_address(item_name)

		self._context.delete_state([address],timeout=self.TIMEOUT)
		self._address_cache[address] = None

	
	# gives all of the state addresses and corresponding state data
	# if you want to fix two things being stored at the same address - fix this method

	# Given an item name, retrieves the state data corresponding to that item
	# If there is no state data corresponding to the state address of the given item 
	# an empty dictionary is returned
	def _load_items(self,item_name):
		address = _make_hw_address(item_name)
		if address in self._address_cache:
			if self._address_cache[address]:
				
				serialized_items = self._address_cache[address]
				items = self._deserialize(serialized_items)
			else:
				items = {}
		else:
			state_entries = self._context.get_state([address],timeout=self.TIMEOUT)
			
			if state_entries :
				self._address_cache[address] = state_entries[0].data
				
				items = self._deserialize(data=state_entries[0].data)

			else:
				self._address_cache[address] = None
				items = {}

		return items

	# Takes serialized state data and decodes the data into a human readable form
	# Deserialized data gives an object of type Item
	def _deserialize(self,data):
		items = {}
		try:
			for item in data.decode().split("|"):
				name,check,c_addr,p_addr = item.split(",")
				items[name] = Item(name,check,c_addr,p_addr)

		except ValueError:
			raise InternalError("Failed to deserialize items data")

		return items

	# Takes item data and serializes it to be stored in the state database
	def _serialize(self, items):
		item_strs =[]
		for name,g in items.items():
			if g.p_addr == None:
				g.p_addr = 'none'
			item_str = ",".join(
				[name,g.check,g.c_addr,g.p_addr])

			item_strs.append(item_str)

		return "|".join(sorted(item_strs)).encode()

	def _deserialize_key(self,data):
		pairs = {}
		try:
			for pair in data.decode().split("|"):
				name,pubkey,profile,role = pair.split(",") # comma is delimiter 
				pairs[name] = Pair(name,pubkey,profile,role)

		except ValueError:
			raise InternalError("Failed to deserialize pairs data")

		return pairs