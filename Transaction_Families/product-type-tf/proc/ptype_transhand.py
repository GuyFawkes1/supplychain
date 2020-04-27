import logging
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from ptype_payload import PtypePayload
from ptype_state import Pair
from ptype_state import PtypeState
from ptype_state import PTYPE_NAMESPACE
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


class WalTransHand(TransactionHandler):

	@property
	def family_name(self):
		return 'wal'

	@property
	def family_versions(self):
		return ['1.0']

	@property
	def namespaces(self):
		return [WAL_NAMESPACE]

	#apply method will be called by the validator

	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key

		walpayload = WalPayload.from_bytes(transaction.payload)
		walstate = WalState(context)

		if walpayload.action == 'delete':

			pair = walstate.get_pair(walpayload.name)

			if pair is None:
				raise InvalidTransaction('Invalid Action')

			walstate.delete_pair(walpayload.name)

		elif walpayload.action == 'create' :
			'''if walstate.get_pair(walpayload.name) is not None:
				raise InvalidTransaction('Invalid Item Exists')
'''			
			try:
				res = subprocess.check_call(['sawtooth','keygen',walpayload.name])
			except:
				pass

			pair = Pair(name = walpayload.name,pubkey = walpayload.pubkey,prof = "X"*5)
			walstate.set_pair(walpayload.name,pair)
		
		elif walpayload.action == 'profile':
			pair = walstate.get_pair(walpayload.name)

			if pair is None:
				raise InvalidTransaction('Invalid Action')

			new_pair = Pair(name=walpayload.name,pubkey = pair.pubkey,prof = walpayload.pubkey)
			print(new_pair)
			walstate.set_pair(walpayload.name,new_pair)