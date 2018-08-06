import logging
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from hw_payload import HwPayload
from hw_state import Item
from hw_state import HwState
from hw_state import HW_NAMESPACE

LOGGER = logging.getLogger(__name__)

# Transaction Handler class for ITEMS
class HwTransHand(TransactionHandler):

	# Returns the family name of the transaction family/transaction type
	@property
	def family_name(self):
		return 'hw'

	# Returns the version number of the transaction family
	@property
	def family_versions(self):
		return ['1.0']

	# Returns the first 6 digits of hexadecimal number of the transaction family
	@property
	def namespaces(self):
		return [HW_NAMESPACE]

	# Apply method will be called by the validator(Inbuilt sawtoth framework)
	# Transaction holds the command that is to be executed
	# Action specified in the transaction parameter is applied and then added to the state. 
	# Context refers to a small piece of the state database
	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key
		hwpayload = HwPayload.from_bytes(transaction.payload)
		hwstate = HwState(context)

		# If action is delete, state data of the item is retrieved from state database and deleted. 
		if hwpayload.action == 'delete':
			item = hwstate.get_item(hwpayload.name)
			if item is None:
				raise InvalidTransaction('Invalid Action')

			hwstate.delete_item(hwpayload.name)

		# If action is create, an object of type Item is created and put into the state database
		# If the item already exists in the state databse, an exception is thrown. 
		elif hwpayload.action == 'create' :

			if hwstate.get_item(hwpayload.name) is not None:
				raise InvalidTransaction('Invalid Item Exists')
			item = Item(name = hwpayload.name,check = "-" * 10,
						c_addr = signer , p_addr = None)
			hwstate.set_item(hwpayload.name,item)
			

		# If action is send, the address of the next person is retrieved
		# The items previous address is set to the current address
		# Its current address is set to the next address
		# The updated item's credentials are updated in the state database. 
		elif hwpayload.action == 'send' :
			item = hwstate.get_item(hwpayload.name)
			if item is None:
				raise InvalidTransaction('Item not yet created')

			# Get's public key of the nxt_add
			# Required to verify if the user exists in database 
			pubkey_nxt_add = hwstate.get_pubkey(name=hwpayload.nxt_add)
			if pubkey_nxt_add is None:
				raise InvalidTransaction('Recvr doesnt exist')

			item.p_addr = item.c_addr
			item.c_addr = pubkey_nxt_add
			hwstate.set_item(hwpayload.name,item)
			_display("Item {} sent to {} by {}".format(hwpayload.name,hwpayload.nxt_add,hwpayload.cu_add))
		

		# When a check is done, the action will be specified as check# 
		# # specifies the number of the check that has been completed
		# Profile of the user that administered the check is searched for 
		# to ensure the check can be authorizes by the user
		# Check is updated into the state database by signifying an x in the checklist
		elif hwpayload.action[:5] == 'check':
			item = hwstate.get_item(hwpayload.name)
			try:
				cno = int(hwpayload.action[5:7])
			except:
				cno = int(hwpayload.action[5])
			prof = hwstate.get_prof(name = hwpayload.cu_add)
			

			if prof == None:
				raise InvalidTransaction('Profile doesnt exist')
			if prof[cno-1] != 'X':
				raise InvalidTransaction('You dont have permission to change this check')
			if hwstate.get_item(hwpayload.name) is None:
				raise InvalidTransaction('Invalid Item does not exist')


			new_c = list("-"*10)
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