"""Manages the data in .ugit directory. Here will be the code that actually touches files on disk."""
import os
import hashlib

UGIT_DIR = '.ugit'  # just like the .git hidden folder on our machines


def init() -> None:
    os.makedirs(UGIT_DIR)
    os.makedirs(f'{UGIT_DIR}/objects')


def hash_object(file_contents, type='blob') -> str:
    """
        Generates and returns hash based on content and type of the file using SHA-1,
        also saves the file at .ugit/objects/hash_of_file.
    """
    type_and_contents = type.encode() + b'\x00' + file_contents
    object_id = hashlib.sha1(type_and_contents).hexdigest()
    with open(f'{UGIT_DIR}/objects/{object_id}', 'wb') as out:
        out.write(type_and_contents)
    return object_id


def get_object(object_id, expected='blob') -> bytes:
    """
        Return bytes of file stored in Object database with object_id hash.
    """
    with open(f'{UGIT_DIR}/objects/{object_id}', 'rb') as stored_file:
        obj = stored_file.read()
    object_type, _, file_contents = obj.partition(b'\x00')
    object_type = object_type.decode()
    if expected is not None:
        assert object_type == expected, f'Expected type {expected}, but got {object_type}'
    return file_contents

