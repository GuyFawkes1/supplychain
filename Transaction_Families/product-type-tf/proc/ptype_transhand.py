import logging
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from ptype_payload import PtypePayload
from ptype_state import Ptype
from ptype_state import PtypeState
from ptype_state import PTYPE_NAMESPACE
import subprocess
LOGGER = logging.getLogger(__name__)

class PtypeTransHand(TransactionHandler):

	@property
	def family_name(self):
		return 'ptype'

	@property
	def family_versions(self):
		return ['1.0']

	@property
	def namespaces(self):
		return [PTYPE_NAMESPACE]

	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key

		ptype_payload = PtypePayload.from_bytes(transaction.payload)
		ptype_state = PtypeState(context)

		
		if ptype_payload.action == "create_product_type":
			if ptype_state.get_ptype(ptype_payload.name) is not None:
				raise InvalidTransaction("Invalid. Product Type Exists")

			product_type = Ptype(ptype_name = ptype_payload.name, dept = ptype_payload.dept, 
			role = None)

			ptype_state.set_ptype(ptype_payload.name, product_type)

		elif ptype_payload.action == "delete_product_type":
			if ptype_state.get_ptype(ptype_payload.name) is None:
				raise InvalidTransaction("Invalid. Product Type Does Not Exist")

			ptype_state.delete_ptype(ptype_payload.name)

		elif ptype_payload.action == "create_role":
			if ptype_state.get_ptype(ptype_payload.name) is None:
				raise InvalidTransaction("Invalid. Must create a Product Type before creating Roles")

			#ptype is of type object Ptype
			# ptype.role is a dictionary
			# check if there is a key for that role existing in the dictionary
			ptype = ptype_state.get_ptype(ptype_payload.name)
			if ptype_payload.role in ptype.role:
				raise InvalidTransaction("Invalid. Role Exists")

			# if ptype_payload.check is None: 
			# 	raise InvalidTransaction("Invalid. Must include at least one Check for role")

			roles = {}
			checks = []
			if ptype_payload.check is not None:
				checks.append(ptype_payload.check)
			roles[ptype_payload.role] = checks

			role_type = Ptype(ptype_name = ptype_payload.name, dept = ptype_payload.dept,
			role = roles)

			ptype_state.set_ptype(ptype_payload.name, role_type)

		elif ptype_payload.action == "delete_role":
			ptype = ptype_state.get_ptype(ptype_payload.name)
			roles = ptype.role
			if ptype_payload.role not in roles:
				raise InvalidTransaction('Invalid. Role does not exist')
			
			del roles[ptype_payload.role]

			role_type = Ptype(ptype_name = ptype_payload.name, dept = ptype_payload.dept,
			role = roles)
			ptype_state.set_ptype(ptype_payload.name, role_type)

		elif ptype_payload.action == "create_check":
			# need to add an exception that a check can only be created if
			# a role has been attached to it

			#check if check already exists
			ptype = ptype_state.get_ptype(ptype_payload.name)
			roles = ptype.role
			checks = roles[ptype_payload.role] # list 
			if ptype_payload.check in checks:
				raise InvalidTransaction("Invalid. Check already exists")

			checks.append(ptype_payload.check)
			roles[ptype_payload.role] = checks

			check_type = Ptype(ptype_name = ptype_payload.name, dept = ptype_payload.dept,
			role = roles)
			ptype_state.set_ptype(ptype_payload.name, check_type)
		
		elif ptype_payload.action == "delete_check":
			ptype = ptype_state.get_ptype(ptype_payload.name)
			roles = ptype.role 
			checks = roles[ptype_payload.role]
			if ptype_payload.check not in checks:
				raise InvalidTransaction("Invalid. Check does not exist")

			checks.remove(ptype_payload.check)
			roles[ptype_payload.role] = checks

			check_type = Ptype(ptype_name = ptype_payload.name, dept = ptype_payload.dept,
			role = roles)
			ptype_state.set_ptype(ptype_payload.name, check_type)

def _display(msg):
	n = msg.count("\n")

	if n>0:
		msg = msg.split("\n")
		length = max(len(line) for line in msg)
	else:
		length = len(msg)
		msg = [msg]

	LOGGER.debug("+"+(length+2)*"-"+"+")
	for line in msg:
		LOGGER.debug("+"+line.center(length)+"+")

	LOGGER.debug("+"+(length+2)*"-"+"+")