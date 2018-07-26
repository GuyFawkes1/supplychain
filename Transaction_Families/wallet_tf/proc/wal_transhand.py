import logging
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from wal_payload import WalPayload
from wal_state import Pair
from wal_state import WalState
from wal_state import WAL_NAMESPACE
import subprocess
LOGGER = logging.getLogger(__name__)

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

# Transaction Handler class for the USER
class WalTransHand(TransactionHandler):

	# Returns the family name of the transaction family
	@property
	def family_name(self):
		return 'wal'

	# Returns the family version of the transaction family
	@property
	def family_versions(self):
		return ['1.0']

	# Returns the first 6 hexadcimal number of the transaction family
	# To be used to create the state address
	@property
	def namespaces(self):
		return [WAL_NAMESPACE]

	# Apply method will be called by the validator(Inbuilt sawtooth framework)
	# Action specified in the transaction parameter is applied and then added to the state
	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key

		walpayload = WalPayload.from_bytes(transaction.payload)
		walstate = WalState(context)

		# If action is delete, state data of the user is retrieved froms state databse and deleted
		if walpayload.action == 'delete':
			pair = walstate.get_pair(walpayload.name)

			if pair is None:
				raise InvalidTransaction('Invalid Action')

			walstate.delete_pair(walpayload.name)

		# If action is create, an object of type Pair is created and put into the state database
		elif walpayload.action == 'create' :
			if walstate.get_pair(walpayload.name) is not None:
				raise InvalidTransaction('Invalid Item Exists')
			# try:
			# 	# creates the key file 
			# 	res = subprocess.check_call(['sawtooth','keygen',walpayload.name])
			# except:
			# 	pass

			pair = Pair(name = walpayload.name,pubkey = walpayload.pubkey,prof = "X"*9,role = walpayload.role)
			walstate.set_pair(walpayload.name,pair)
		
		# If the action is profile, a profile pertaining to what checks can be administered by this user are created
		elif walpayload.action == 'profile':
			pair = walstate.get_pair(walpayload.name)

			if pair is None:
				raise InvalidTransaction('Invalid Action')

			new_pair = Pair(name=walpayload.name,pubkey = pair.pubkey,prof = walpayload.pubkey,role = walpayload.role)
		
			walstate.set_pair(walpayload.name,new_pair)