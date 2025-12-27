"""Manages the data in .ugit directory. Here will be the code that actually touches files on disk."""
import os
import hashlib

UGIT_DIR = '.ugit'  # just like the .git hidden folder on our machines


def init():
    os.makedirs(UGIT_DIR)


def hash_object(data):
    """
        Generates hash based on content of the file using SHA-1,
        and saves the file at .ugit/objects/hash_of_file.
    """
    object_id = hashlib.sha1(data).hexdigest()
    with open(f'{UGIT_DIR}/objects/{object_id}', 'wb') as out:
        out.write(data)
    return object_id

