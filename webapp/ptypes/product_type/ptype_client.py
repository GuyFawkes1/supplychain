import hashlib
import base64
from base64 import b64encode
import time
import datetime
import requests
import yaml
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_xo.xo_exceptions import XoException


def _sha512(data):
	return hashlib.sha512(data).hexdigest()


class PtypeClient:
	def __init__(self, base_url, keyfile = None):
		self._base_url = base_url

		if keyfile is None:
			self._signer = None
			return

		try:
			with open(keyfile) as fd:
				private_key_str = fd.read().strip()

		except OSError as err:
			raise XoException('Failed to read private key {} : {}'.format(
				keyfile,str(err)))

		try :
			private_key = Secp256k1PrivateKey.from_hex(private_key_str)

		except ParseError as e :
			raise XoException('Unable to load priv key')

		self._signer = CryptoFactory(create_context('secp256k1')) \
			.new_signer(private_key)

	
	# def _send_hw_txn(self, name, dept, role, check, action, wait=None):
	def create_product_type(self, name, dept, wait = None):
		return self._send_hw_txn(name = name, dept = dept, role = None, check = None,
		action = "create_product_type", wait = wait)

	def delete_product_type(self, name, dept, wait = None):
		return self._send_hw_txn(name = name, dept = dept, role = None, check = None,
		action = "delete_product_type", wait = wait)

	def create_role(self, name, dept, role, check, wait = None):
		return self._send_hw_txn(name = name, dept = dept, role = role, check = check,
		action = "create_role", wait = wait)

	def delete_role(self, name, dept, role, wait = None):
		return self._send_hw_txn(name = name, dept = dept, role = role, check = None,
		action = "delete_role", wait = wait)

	def create_check(self, name, dept, role, check, wait = None):
		return self._send_hw_txn(name = name, dept = dept, role = role, check = check,
		action = "create_check", wait = wait)

	def delete_check(self, name, dept, role, check, wait = None):
		return self._send_hw_txn(name = name, dept = dept, role = role, check = check,
		action = "delete_check", wait = wait)

	def show(self, name):
		address = self._get_address(name)
		result = self._send_request(
			"state/{}".format(address),
			name = name)
		try:
			return base64.b64decode(yaml.safe_load(result)["data"])

		except BaseException:
			return None

	def _get_status(self, batch_id):
		try:
			result = self._send_request(
			'batch_statuses?id={}'.format(batch_id))
			return yaml.safe_load(result)['data'][0]['status']
		except BaseException as err:
			raise XoException(err)

	def _get_prefix(self):
		return _sha512('ptype'.encode('utf-8'))[0:6]

	def _get_address(self, name):
		ptype_prefix = self._get_prefix()
		item_address = _sha512(name.encode('utf-8'))[0:64]
		return ptype_prefix + item_address

	# potentially not required because txn is not being sent to someone else
	# def _get_key_address(self, name):
	# 	wal_prefix =  _sha512('wal'.encode('utf-8'))[0:6]
	# 	key_address = _sha512(name.encode('utf-8'))[0:64]
	# 	return wal_prefix + key_address


	def _send_request(self, suffix, data=None, content_type=None, name=None):
		if self._base_url.startswith("http://"):
			url = "{}/{}".format(self._base_url, suffix)
		else:
			url = "http://{}/{}".format(self._base_url, suffix)

		headers  = {}

		if content_type is not None:
			headers['Content-Type'] = content_type

		try:
			if data is not None:
				result = requests.post(url, headers= headers, data=data)
			else:
				result = requests.get(url, headers=headers)
			if result.status_code == 404:
				raise XoException("No such item: {}".format(name))
			elif not result.ok:
				raise XoException("Error {}:{}".format(result.status_code, result.reason) )

		except requests.ConnectionError as err:
			raise XoException('Failed to connect to {}:{}'.format(url, str(err)))


		except BaseException as err:
			raise XoException(err)

		return result.text

	# DONE UP TILL HERE

	def _send_hw_txn(self, name, dept, role, check, action, wait=None):
		ts = time.time()
		time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%X %x')
		payload = ",".join([name, dept, role, check, action, time_stamp]).encode()
		
		# OLD
		#payload = ",".join([name,action,cu_add,nxt_add,time_stamp]).encode()
		# key_add = self._get_key_address(nxt_add)
		# cli_add = self._get_key_address(cu_add)
		address = self._get_address(name)

		
		#for a transaction processor to access an address in the state database, we have to specify it in
		#inputs of the transaction header. For a transaction processor to change an element at an address,
		#we have to specify that address in outputs
		# if key_add is not None:
		# 	header = TransactionHeader(
		# 		signer_public_key = self._signer.get_public_key().as_hex(),
		# 		family_name = "ptype",
		# 		family_version = "1.0",
		# 		inputs = [address,key_add,cli_add], 
		# 		outputs = [address],				 	
		# 		dependencies = [],
		# 		payload_sha512 = _sha512(payload),
		# 		batcher_public_key = self._signer.get_public_key().as_hex(),
		# 		nonce = time.time().hex().encode()).SerializeToString()
			
		# else:
		header = TransactionHeader(
			signer_public_key = self._signer.get_public_key().as_hex(),
			family_name = "ptype",
			family_version = "1.0",
			inputs = [address], 
			outputs = [address], 
			dependencies = [],
			payload_sha512 = _sha512(payload),
			batcher_public_key = self._signer.get_public_key().as_hex(),
			nonce = time.time().hex().encode()).SerializeToString()
			
		signature = self._signer.sign(header)

		transaction = Transaction(header= header,payload = payload,
			header_signature = signature)
		
		batch_list = self._create_batch_list([transaction])
		batch_id = batch_list.batches[0].header_signature
		wait = 1.5
		if wait and wait > 0:
			wait_time = 0
			start_time = time.time()
			response = self._send_request(
				"batches",batch_list.SerializeToString(),
				'application/octet-stream')
			while wait_time <wait:
				status = self._get_status(batch_id)
				wait_time = time.time()-start_time

				if status != 'PENDING':
					return response
	
			return response

		
		return self._send_request("batches",batch_list.SerializeToString(),
			'application/octet-stream')

	#transactions are wrapped as batches. We wait some time to recieve any transactions to come by
	#If wait time is over , we complete the batch with the transactions recieved until that point and
	#wrap up the batch creation and push it into the validator rest-api


	def _create_batch_list(self,transactions):
		transaction_signatures = [t.header_signature for t in transactions]

		header = BatchHeader(signer_public_key = self._signer.get_public_key().as_hex(),
			transaction_ids = transaction_signatures).SerializeToString()

		signature = self._signer.sign(header)

		batch = Batch(
			header = header,
			transactions= transactions,
			header_signature = signature)
		return BatchList(batches = [batch])
