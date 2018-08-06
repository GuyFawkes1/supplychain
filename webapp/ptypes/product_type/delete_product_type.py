import os
from .ptype_client import PtypeClient

def _get_keyfile(adminname):
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, adminname)

def delete_ptype(name, dept, adminname, url):
    keyfile = _get_keyfile(adminname)
    ptype_client = PtypeClient(base_url = url, keyfile = keyfile)
    response = ptype_client.delete_product_type(name = name, dept = dept)
    return response