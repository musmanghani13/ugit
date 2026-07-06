# ugit: DIY Git in Python

A minimal reimplementation of Git, written from scratch in Python. Built by following [ugit: DIY Git in Python](https://www.leshenko.net/p/ugit/) by Nikita Leshenko, as a way to understand how Git actually works under the hood, content-addressable storage, trees, commits, refs, and branches; without any of the magic.

> Please note that this is a learning project, not a Git replacement. Don't trust it with anything you can't afford to lose.

## How it works

ugit stores everything in a `.ugit/` directory (analogous to `.git/`):

- **Objects** Every file is hashed with SHA-1 and stored by its hash in `.ugit/objects/`. Objects are typed: `blob` (file contents), `tree` (a directory snapshot), and `commit` (a tree + parent + message).
- **Refs** Branches and tags are just tiny files pointing at a commit hash. `HEAD` points at the current branch or commit.
- **Commits** A commit records a snapshot of the whole working tree plus a pointer to its parent, forming the history chain that `log` walks.

## Project structure

```
ugit/
├── setup.py          # Package definition; installs the `ugit` command
└── ugit/
    ├── cli.py        # Argument parsing; maps subcommands to functions
    ├── base.py       # Higher-level logic: trees, commits, branches
    └── data.py       # Low-level storage: the .ugit object database and refs
```

## Installation

Requires Python 3. From the repo root:

```bash
pip install -e .
```

This installs the `ugit` command in development mode, so code changes take effect immediately.

## Usage

```bash
# Start a repository
mkdir my-project && cd my-project
ugit init

# Snapshot your work
ugit commit -m "First commit"

# View history
ugit log

# Plumbing commands (peek under the hood)
ugit hash-object <file>     # Store a file, print its hash
ugit cat-file <hash>        # Print a stored object
ugit write-tree             # Store the current directory as a tree
ugit read-tree <hash>       # Restore a tree into the working directory

# Move around history
ugit checkout <commit>
ugit tag <name> [<commit>]
ugit branch <name> [<start-point>]
```

(I am still working on this project. Please run `ugit --help` to see what's currently available.)
