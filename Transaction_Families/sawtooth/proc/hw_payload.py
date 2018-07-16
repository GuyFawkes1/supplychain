from sawtooth_sdk.processor.exceptions import InvalidTransaction

# Encrypted string from the transaction payload is decoded
# Individual components from the decoded string are extracted
# Individual methods return the attributes that are called by hw_transhand.py

class HwPayload(object):

	def __init__(self,payload):

		# Encoded string is decoded and split into its individual components
		try:
			name,action,cu_add,nxt_add,time_stamp = payload.decode().split(",")
		except ValueError:
			raise InvalidTransaction("Invalid payload serialization")
		
		self._name = name
		self._action = action
		self._cu_add = cu_add
		self._nxt_add = nxt_add
		self._time_stamp = time_stamp
 
	# Returns the HWPayload class and its initialized fields
	@staticmethod
	def from_bytes(payload):
		return HwPayload(payload=payload)

	# Returns the name of the item
	@property
	def name(self):
		return self._name
	
	# Returns the action that was led to the transaction
	@property
	def action(self):
		return self._action

	# Returns the human readable form of the user who initiated the transaction
	# and currently held the item 
	@property
	def cu_add(self):
		return self._cu_add
	
	# Returns the human readable form of the user who will receive the item next
	# and who the results of the transaction are sent to when required
	@property
	def nxt_add(self):
		return self._nxt_add

	# Returns the time stamp of the transaction 
	@property
	def time_stamp(self):
		return self._time_stamp
	