import hashlib
from sawtooth_sdk.processor.exceptions import InternalError

# 128-digit hexadecimal number for the first 6 digits of each transaction family is created
# The first 6 digits from the number is extracted
# This will correspond to the transaction family in the state adresss
PTYPE_NAMESPACE = hashlib.sha512('ptype'.encode("utf-8")).hexdigest()[0:6]

# Complete state address is created 
# Using the 6 digits corresponding to transaction family 
# And first 64 digits from the hexadecimal number for the item
def _make_pt_address(name):
	return PTYPE_NAMESPACE + \
		hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

# Ptype object that contains the product type name, the role of the person 
# who sent the transaction and the next person who will receive the transaction
# and the checks that have been compeleted for the product type
class Ptype(object):
	def __init__(self, ptype_name, dept, role):
		self.name = ptype_name # name of product type
		self.dept = dept # dept for whose checks + roles have been administered 
		self.role = role  # role that has been added 

	@property
	def name(self):
		return self.name

	@property
	def dept(self):
		return self.dept

	@property
	def role(self):
		return self.role


class PtypeState(object):
	TIMEOUT = 3
	def __init__(self,context):
		self._context = context
		self._address_cache = {}

	def _deserialize(self, data):
		ptype = {}
		try:
			for types in data.decode().split("|"):
				name, dept, role = types.split(",") # potential problem? splitting roles?
				ptype[name] = Ptype(name, dept, role)
		except ValueError:
			raise InternalError("Failed to deserialize product type data")
		return ptype

	# fix! 
	def _serialize(self, ptypes): 
		ptype_strs = []
		for name, g in ptypes.items(): 
			if g.n_role == None:
				g.n_role = 'none'
			string = ",".join([name, g.role, g.checks])

			ptype_strs.append(string)
		return "|".join(sorted(ptype_strs)).encode()

	def load_ptypes(self, ptype_name):
		address = _make_pt_address(ptype_name)
		if address in self._address_cache:
			if self._address_cache[address]:
				serialized_ptypes = self._address_cache[address]
				ptypes = self._deserialize(serialized_ptypes)
			else: 
				ptypes = {}
		else:
			state_entries = self._context.get_state([address],timeout=self.TIMEOUT)
			if state_entries:
				self._address_cache[address] = state_entries[0].data
				
				ptypes = self._deserialize(data=state_entries[0].data)

			else:
				self._address_cache[address] = None
				ptypes = {}

		return ptypes

	def get_ptype(self, ptype_name):
		return self.load_ptypes(ptype_name = ptype_name).get(ptype_name)

	def set_ptype(self, ptype_name, ptype):
		ptypes = self.load_ptypes(ptype_name = ptype_name)

		ptypes[ptype_name] = ptype
		self.store_ptype(ptype_name = ptype_name, ptype = ptypes)

	def store_ptype(self, ptype_name, ptype):
		address = _make_pt_address(ptype_name)
		state_data = self._serialize(ptype)

		self._address_cache[address] = state_data
		self._context.set_state({address: state_data}, timeout = self.TIMEOUT)

	def delete_ptype(self, ptype_name):
		ptypes = self.load_ptypes(ptype_name = ptype_name)

		del ptypes[ptype_name]
		if ptypes:
			self.store_ptype(ptype_name, ptypes)
		else:
			self._delete_ptype(ptype_name = ptype_name)
	
	def _delete_ptype(self, ptype_name):
		address = _make_pt_address(ptype_name)

		self._context.delete_state([address], timeout = self.TIMEOUT)
		self._address_cache[address] = None