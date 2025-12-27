import os
from collections import namedtuple

from . import data

Commit = namedtuple('Commit', ['tree', 'parent', 'message'])


def write_tree(directory='.', verbose=False):
    """ 
        This command will take the current working directory and store it to the object database recursively.
        If hash-object was for storing an individual file, then write-tree is for storing a whole directory.
    """
    entries: list = []
    _type: str = None
    with os.scandir(directory) as directory_iterator:
        for entry in directory_iterator:
            location = f'{directory}/{entry.name}'
            if ignore(location):
                continue
            if entry.is_file (follow_symlinks=False):
                # found a file, so we save this as 'blob <hash> file_name'
                _type = 'blob'
                with open(location, 'rb') as f:
                    stored_object_id = data.hash_object(f.read(), type='blob')
                    if verbose:
                        print(f'blob\t{stored_object_id}\t{location}')
            elif entry.is_dir (follow_symlinks=False):
                # found a directory, so we save this as 'tree <hash> dir_name'
                _type = 'tree'
                stored_object_id = write_tree(location, verbose) # move inside the folder and look for files.
                if verbose:
                    print(f'tree\t{stored_object_id}\t{location}')
            entries.append((entry.name, stored_object_id, _type))
    tree = ''.join(
        f'{o_type} {oid} {o_name}\n'    # string of files inside a directory
        for o_name, oid, o_type in sorted(entries)
    )
    return data.hash_object(tree.encode(), 'tree')


def commit(message: str, verbose=False):
    """
        Creates a commit object in object database with the following structure
        
        tree hash
        
        parent hash

        This is the commit message!
    """
    commit_object: str = ''

    commit_object += f'tree\t{write_tree(verbose=verbose)}\n'
    HEAD = data.get_HEAD()
    if HEAD:
        commit_object += f'parent\t{HEAD}\n'
    commit_object += '\n'
    commit_object += f'{message}\n'

    commit_id: str = data.hash_object(commit_object.encode(), type='commit')
    data.set_HEAD(commit_id)
    return commit_id


def get_commit(object_id: str) -> Commit:
    message: str = None
    parent: str = None
    tree: str = None

    commit_object = data.get_object(object_id, expected='commit').decode()
    lines = commit_object.splitlines()
    for line in lines:
        line = line.split('\t')
        if line[0] == 'tree':
            tree = line[1]
        elif line[0] == 'parent':
            parent = line[1]
        elif len(line) == 1:
            message = line[0]
    return Commit(tree=tree, parent=parent, message=message)


def _iter_tree_entries(object_id):
    """
        Takes an OID of a tree, tokenize it line-by-line and yield the raw string values.
    """
    if not object_id:
        return
    tree = data.get_object(object_id=object_id, expected='tree')
    for entry in tree.decode().splitlines():
        _type, oid, name = entry.split(' ', 2)
        yield _type, oid, name


"""
The code below works as follows..

1. _iter_tree_entries('root111')
2. Read .ugit/objects/root111
3. Content: b'tree\x00blob abc123 cat.txt\nblob def456 dog.txt\ntree xyz999 others\n'
4. Extract after \x00: b'blob abc123 cat.txt\nblob def456 dog.txt\ntree xyz999 others\n'
5. Decode to string and split lines:
    ['blob abc123 cat.txt', 'blob def456 dog.txt', 'tree xyz999 others']
6. Parse each line:
    Yield ('blob', 'abc123', 'cat.txt')
    Yield ('blob', 'def456', 'dog.txt')
    Yield ('tree', 'xyz999', 'others')  ← This tells get_tree() to recurse and call _iter_tree_entries for xyz999
"""
def get_tree(oid, base_path=''):
    """
        Parse a tree into dictionary.
    """
    result = {}
    for _type, oid, name in _iter_tree_entries(object_id=oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if _type == 'blob':
            result[path] = oid
        elif _type == 'tree':
            result.update(get_tree(oid=oid, base_path=f'{path}/'))
        else:
            assert False, f'Unknown tree entry {_type}'
    return result


def _empty_current_dir():
    for root, dirnames, filenames in os.walk('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath(f'{root}/{filename}')
            if ignore(path):
                continue
            os.remove(path=path)
        for dirname in dirnames:
            path = os.path.relpath(f'{root}/{dirname}')
            if ignore(path):
                continue
            try:
                os.rmdir(path=path)
            except (FileNotFoundError, OSError):
                pass


def read_tree(tree_oid):
    _empty_current_dir()
    for path, oid in get_tree(tree_oid, base_path='./').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)     # Even if any file was deleted it will be restored :)
        with open(path, 'wb') as f:
            f.write(data.get_object(oid, expected='blob'))  # we are writing the file content here.


def ignore(path) -> bool:
    normalized_path = path.replace('\\', '/')
    current_path_split = normalized_path.split('/')
    if '.ugit' in current_path_split:   # ignore the .ugit folder. Remember .ugit is equivilant of .git folder when we run git init.
        return True
    elif '.venv' in current_path_split: # ignore .venv for obvious reasons.
        return True
    elif '.git' in current_path_split:  # ignore the actual .git folder for this project.
        return True
    return False

