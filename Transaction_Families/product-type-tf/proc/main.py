from sawtooth_sdk.processor.core import TransactionProcessor
from ptype_transhand import PtypeTransHand
import argparse
#add a processor handler

parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()
processor = TransactionProcessor(url=args.url)
handler = PtypeTransHand()
processor.add_handler(handler)
processor.start()
