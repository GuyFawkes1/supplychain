from sawtooth_sdk.processor.exceptions import InvalidTransaction

class PtypePayload(object):

	def __init__(self,payload):

		try:
			name, dept, role, check, action, time_stamp = payload.decode().split(",")
		except ValueError:
			raise InvalidTransaction("Invalid payload serialization")

		self._name = name 
		self._dept = dept
		self._role = role 
		self._check = check
		self._action = action
		self._time_stamp = time_stamp

	@staticmethod
	def from_bytes(payload):
		return PtypePayload(payload=payload)

	# Returns the product type name of the item 
	@property
	def name(self):
		return self._name

	# Returns the department the user(admin) who made the transaction is in
	@property
	def dept(self):
		return self._dept

	# Returns the name of the role the admin is creating 
	@property
	def role(self):
		return self._role

	# Returns the desrcription of the check the admin is creating a check
	@property
	def check(self):
		return self._check

	# Returns the action that was led to the transaction being created
	@property
	def action(self):
		return self._action

	# Returns the time stamp of the transaction
	@property
	def time_stamp(self):
		return self._time_stamp



# The admin is creating the user and the role the user will have
# creating user + specifying role is one transaction (action - create user)
# changing role is another transaction (action - change role)
# deleting the user and their role is another transaction (action - delete user)

# adding checks is another transaction (action - checks)
# deleting a check is another transaction (action - delete check)

# creating a product type is one transaction (action - create)

# NOTES:
# wal is creating the user
# *** probably want to assign the role for the user here ***
# hw is creating/deleting the item + updating checks that have been done


# creating checks for products
# creating roles for their respective departments