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

# class for the item's individual state date
class Item(object):
	def __init__(self,name,check,c_addr,p_addr):
		self.name = name
		self.check = check
		self.c_addr = c_addr
		self.p_addr = p_addr

# not item but for user 
class Pair(object):
	def __init__(self,name,pubkey,prof):
		self.name = name
		self.prof = prof
		self.pubkey = pubkey


# if any changes need 
# receives the individual state data and either adds the new state data to the new state address
# or replaces state data with the most current stuff 
class HwState(object):
	
	TIMEOUT = 3

	def __init__(self,context):
		self._context = context
		self._address_cache = {}

	# items is dictionary of key value pairs - key being the address and value being the state data
	# there may be an exception where one address has data for two things - the if else handles that
	def delete_item(self,item_name):
		items = self._load_items(item_name = item_name)

		del items[item_name]
		if items:
			self._store_item(item_name,items = items)
		else:
			self._delete_item(item_name)

	# used in transhand to retrieve public key
	def get_pubkey(self,name):
		key_address = _make_wal_address(name)
		key_state_entry=self._context.get_state([key_address],timeout=self.TIMEOUT)
		
		if key_state_entry :
			pubkey = self._deserialize_key(data=key_state_entry[0].data)
			return pubkey[name].pubkey
		else:
			print("Reciever doesn't exist in the database")
			return None

	def get_prof(self,name):
		key_address = _make_wal_address(name)
		key_state_entry=self._context.get_state([key_address],timeout=self.TIMEOUT)
		
		if key_state_entry :
			pubkey = self._deserialize_key(data=key_state_entry[0].data)
			return pubkey[name].prof

		else:

			print("Reciever doesn't exist in the database")
			return None

	# puts individual state item into state database
	def set_item(self,item_name,item):
		items = self._load_items(item_name= item_name)

		items[item_name] = item

		self._store_item(item_name,items = items)

	# retrieves individual state data from database
	def get_item(self,item_name):
		return self._load_items(item_name=item_name).get(item_name)

	# puts back a dictionary of strings
	def _store_item(self,item_name,items):

		address = _make_hw_address(item_name)

		state_data = self._serialize(items)

		self._address_cache[address] = state_data
		self._context.set_state({address: state_data},timeout=self.TIMEOUT)

	def _delete_item(self,item_name):
		address = _make_hw_address(item_name)

		self._context.delete_state([address],timeout=self.TIMEOUT)
		self._address_cache[address] = None

	# gives all of the state addresses and corresponding state data
	# if you want to fix two things being stored at the same address 
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

	# splits into individual components
	def _deserialize(self,data):
		items = {}
		try:
			for item in data.decode().split("|"):
				name,check,c_addr,p_addr = item.split(",")
				items[name] = Item(name,check,c_addr,p_addr)

		except ValueError:
			raise InternalError("Failed to deserialize items data")

		return items

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
				name,pubkey,profile = pair.split(",") # comma is delimiter 
				pairs[name] = Pair(name,pubkey,profile)

		except ValueError:
			raise InternalError("Failed to deserialize pairs data")

		return pairs