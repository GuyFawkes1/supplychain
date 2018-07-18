from sawtooth_sdk.processor.exceptions import InvalidTransaction

class PtypePayload(object):

	def __init__(self,payload):

		try:
			name, ptype, role, action, cu_add, nxt_add, time_stamp = payload.decode().split(",")
		except ValueError:
			raise InvalidTransaction("Invalid payload serialization")

		self._name = name
		self._ptype = ptype
		self._role = role
		self._action = action
		self._cu_add = cu_add
		self._nxt_add = nxt_add
		self._time_stamp = time_stamp

	@staticmethod
	def from_bytes(payload):
		return PtypePayload(payload=payload)

	# Returns the name of the item 
	@property
	def name(self):
		return self._name

	# Returns the product type name of the item
	@property
	def ptype(self):
		return self._ptype

	# Returns the role of the user who made the transaction
	@property
	def role(self):
		return self._role

	# Returns the action that was led to the transaction being created
	@property
	def action(self):
		return self._action

	# Returns the human readable form of the user who initiated the transaction
	# and the user who currently held the item 
	@property
	def cu_add(self):
		return self._cu_add

	# Returns the human readable form of the user who will receive the item next
	# and who the results of the transaction are sent to
	@property
	def nxt_add(self):
		return self._nxt_add

	# Returns the time stamp of the transaction
	@property
	def time_stamp(self):
		return self._time_stamp