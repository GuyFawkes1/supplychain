from sawtooth_sdk.processor.exceptions import InvalidTransaction

# Encrypted string from the transaction payload is decoded
# Individual components from the decoded string are extracted
# Individual methods return the attributes that are called by wal_transhand.py

class WalPayload(object):

	def __init__(self,payload):

		# Encoded string is decoded and split into its individual components
		try:
			name,action,pubkey,dept,role,time_stamp = payload.decode().split(",")
		except ValueError:
			raise InvalidTransaction("Invalid payload serialization")

		self._name = name
		self._action = action
		self._pubkey = pubkey
		self._dept = dept
		self._role = role
		self._time_stamp = time_stamp

	# Returns the WalPayload class and its initialized fields
	@staticmethod
	def from_bytes(payload):
		return WalPayload(payload=payload)

	# Returns the name of the user
	@property
	def name(self):
		return self._name
	
	# Returns the action the user has administered
	@property
	def action(self):
		return self._action

	# Returns the public key of the user
	@property
	def pubkey(self):
		return self._pubkey

	# Returns the dept the user is a part of
	def dept(self):
		return self._dept

	# Returns the role of the user
	@property
	def role(self):
		return self._role

	# Returns the time stamp of the transaction 
	@property
	def time_stamp(self):
		return self._time_stamp