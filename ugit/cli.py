import os
import argparse
import sys

from . import base
from . import data

def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.add_argument('file')
    hash_object_parser.set_defaults(func=hash_object)

    cat_file_parser = commands.add_parser('cat-file')
    cat_file_parser.add_argument('object_id')
    cat_file_parser.set_defaults(func=cat_file)

    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree')
    read_tree_parser.add_argument('tree')
    read_tree_parser.set_defaults(func=read_tree)

    commit_parser = commands.add_parser('commit')
    commit_parser.add_argument('-m', '--message', required=True)
    commit_parser.set_defaults(func=commit)

    return parser.parse_args()


def init(args):
    print('Attempting to create .ugit')
    data.init()
    print(f'Initialized empty ugit repository at {os.getcwd()}.')


def hash_object(args):
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object_id, expected=None))


def write_tree(args):
    working_directory_tree = base.write_tree()
    print(f'Saved current working directory: {os.getcwd()} with root tree hash: {working_directory_tree}')


def commit(args):
    print(base.commit(args.message))


def read_tree(args):
    base.read_tree(args.tree)

