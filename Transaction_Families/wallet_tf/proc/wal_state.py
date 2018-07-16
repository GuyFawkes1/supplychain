import hashlib
from sawtooth_sdk.processor.exceptions import InternalError

WAL_NAMESPACE = hashlib.sha512('wal'.encode("utf-8")).hexdigest()[0:6]

def _make_wal_address(name):
	return WAL_NAMESPACE + \
		hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

# User object that includes their name, profile (checks that can be completed by them)
# and their public key
# Individual state data stored in the user's state database is created via this object
class Pair(object):
	def __init__(self,name,pubkey,prof):
		self.name = name
		self.pubkey = pubkey
		self.prof = prof

# Object parameter receives individual state data
# Either adds new state data with a new state address to the state database
# Or replaces existing state data at the user's state address with the most current data
# Actions denoted by transactions are implemented here
class WalState(object):
	TIMEOUT = 3
	def __init__(self,context):
		self._context = context
		self._address_cache = {}

	# Deletes the instance of the user from the dictionary of state addresses to state data	
	def delete_pair(self,pair_name):
		# Dictionary where keys are the state address and the value is the state data
		pairs = self._load_pairs(pair_name= pair_name)

		del pairs[pair_name]
		if pairs:
			self._store_pair(pair_name,pairs = pairs)
		else:
			self._delete_pair(pair_name)

	# Sets the item to its corresponding state address
	def set_pair(self,pair_name,pair):
		pairs = self._load_pairs(pair_name= pair_name)
		pairs[pair_name] = pair
		self._store_pair(pair_name,pairs = pairs)

	# Retrieves the individual state data for the user from the state database
	def get_pair(self,pair_name):
		return self._load_pairs(pair_name=pair_name).get(pair_name)

	# Serializes state data and stores the data with its corresponding
	# state address in the state database
	def _store_pair(self,pair_name,pairs):

		address = _make_wal_address(pair_name)
		sec_add = _make_wal_address(pairs[pair_name].pubkey)
		state_data = self._serialize(pairs)
		self._address_cache[address] = state_data
		self._address_cache[sec_add] = state_data
		self._context.set_state({address: state_data},timeout=self.TIMEOUT)
		
		#Unresolved issue when setting the profile... Leading to change of profile at only one state table
		try:
			self._context.set_state({sec_add: state_data},timeout=self.TIMEOUT)
		except:
			pass

	# Deletes state data for a user and its state address from the state database
	def _delete_pair(self,pair_name):
		address = _make_wal_address(pair_name)
		self._context.delete_state([address],timeout=self.TIMEOUT)
		self._address_cache[address] = None

	# Given an item name, retrieves the state data corresponding to that item
	# If there is no state data corresponding to the state address of the given item
	# an empty dictionary is returned
	def _load_pairs(self,pair_name):
		address = _make_wal_address(pair_name)
		if address in self._address_cache:
			if self._address_cache[address]:
				serialized_pairs = self._address_cache[address]
				pairs = self._deserialize(serialized_pairs)
			else:
				pairs = {}
		else:
			state_entries = self._context.get_state([address],timeout=self.TIMEOUT)
			
			if state_entries :
				self._address_cache[address] = state_entries[0].data
				
				pairs = self._deserialize(data=state_entries[0].data)

			else:
				self._address_cache[address] = None
				pairs = {}

		return pairs

	# Takes serialized state data and decodes the data into a human readable form
	# Deserialized data gives an object of type Pair
	def _deserialize(self,data):
		pairs = {}
		try:
			for pair in data.decode().split("|"):
				name,pubkey,prof = pair.split(",")
				pairs[name] = Pair(name,pubkey,prof)

		except ValueError:
			raise InternalError("Failed to deserialize pairs data")

		return pairs

	# Takes user data and serializes it to be stored in the state database
	def _serialize(self, pairs):
		pair_strs =[]
		for name,g in pairs.items():
			pair_str = ",".join(
				[name,g.pubkey,g.prof])

			pair_strs.append(pair_str)

		return "|".join(sorted(pair_strs)).encode()