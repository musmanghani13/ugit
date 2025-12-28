"""Manages the data in .ugit directory. Here will be the code that actually touches files on disk."""
import os
import hashlib

UGIT_DIR = '.ugit'  # just like the .git hidden folder on our machines


def init() -> None:
    os.makedirs(UGIT_DIR)
    os.makedirs(f'{UGIT_DIR}/objects')


def hash_object(data, type='blob') -> str:
    """
        Generates and returns hash based on content and type of the file using SHA-1,
        also saves the file at .ugit/objects/hash_of_file.
    """
    type_and_contents = type.encode() + b'\x00' + data
    object_id = hashlib.sha1(type_and_contents).hexdigest()
    with open(f'{UGIT_DIR}/objects/{object_id}', 'wb') as out:
        out.write(type_and_contents)
    return object_id


def get_object(object_id, expected='blob') -> bytes:
    """
        Return bytes of data stored in Object database with object_id hash.
    """
    with open(f'{UGIT_DIR}/objects/{object_id}', 'rb') as stored_data:
        obj = stored_data.read()
    object_type, _, data = obj.partition(b'\x00')
    object_type = object_type.decode()
    if expected is not None:
        assert object_type == expected, f'Expected type {expected}, but got {object_type}'
    return data     # in case of tree, this data will be the file files inside the directory with object_id passed. As saved on line 31 base.py write_tree function


def set_ref(ref: str, commit_id: str) -> None:
    """
        Associates a commit id to a ref.
        Value of ref can be a user defined value of HEAD. Depending on
        the context this function is called.
    """
    ref_path = f'{UGIT_DIR}/{ref}'
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(commit_id)


def get_ref(ref: str) -> str:
    """
        Returns the commit id associated with a ref.
    """
    ref_path: str = f'{UGIT_DIR}/{ref}'
    if os.path.isfile(ref_path):
        with open(ref_path, 'r') as ref_file:
            return ref_file.read().strip()

