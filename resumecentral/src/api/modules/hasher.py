import hashlib
import pickle
from uuid import uuid4

def object_to_bytes(obj):
    return pickle.dumps(obj)

def compute_hash(obj):
    byte_representation = object_to_bytes(obj)
    hash_object = hashlib.sha256(byte_representation)
    return hash_object.hexdigest()

def secret_key():
    return uuid4()    

