import logging
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from hw_payload import HwPayload
from hw_state import Item
from hw_state import HwState
from hw_state import HW_NAMESPACE

LOGGER = logging.getLogger(__name__)

class HwTransHand(TransactionHandler):

	@property
	def family_name(self):
		return 'hw'

	@property
	def family_versions(self):
		return ['1.0']

	@property
	def namespaces(self):
		return [HW_NAMESPACE]

	#apply method will be called by the validator(Inbuilt sawtoth framework)

	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key
		hwpayload = HwPayload.from_bytes(transaction.payload)
		hwstate = HwState(context)

		if hwpayload.action == 'delete':
			item = hwstate.get_item(hwpayload.name)
			if item is None:
				raise InvalidTransaction('Invalid Action')

			hwstate.delete_item(hwpayload.name)


		elif hwpayload.action == 'create' :

			if hwstate.get_item(hwpayload.name) is not None:
				raise InvalidTransaction('Invalid Item Exists')
			item = Item(name = hwpayload.name,check = "-" * 4 ,
						c_addr = signer , p_addr = None)
			hwstate.set_item(hwpayload.name,item)
			


		elif hwpayload.action == 'send' :
			item = hwstate.get_item(hwpayload.name)
			if item is None:
				raise InvalidTransaction('Item not yet created')

			#get pubkey of the nxt_add
			pubkey_nxt_add = hwstate.get_pubkey(name=hwpayload.nxt_add)
			if pubkey_nxt_add is None:
				raise InvalidTransaction('Recvr doesnt exist')

			item.p_addr = item.c_addr
			item.c_addr = pubkey_nxt_add
			hwstate.set_item(hwpayload.name,item)
			_display("Item {} sent to {} by {}".format(hwpayload.name,hwpayload.nxt_add,hwpayload.cu_add))
		
		elif hwpayload.action[:5] == 'check':
			print(hwpayload.cu_add)
			item = hwstate.get_item(hwpayload.name)
			cno = int(hwpayload.action[5])
			print("Inside transhand")
			print(hwpayload.cu_add)
			prof = hwstate.get_prof(name = hwpayload.cu_add)
			

			if prof == None:
				raise InvalidTransaction('Profile doesnt exist')
			if prof[cno-1] != 'X':
				raise InvalidTransaction('You dont have permission to change this check')
			if hwstate.get_item(hwpayload.name) is None:
				raise InvalidTransaction('Invalid Item does not exist')


			new_c = list("-"*4)
			for i in range(0,len(item.check)):
				if i != cno-1:
					new_c[i] = item.check[i] 
				else:
					new_c[i] = 'x'
			new_c = "".join(new_c)

			item1 = Item(name = hwpayload.name,check =new_c,
						c_addr = item.c_addr , p_addr = item.p_addr)
			hwstate.set_item(hwpayload.name,item1)


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