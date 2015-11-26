#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copy a file to all directories on same level that contain same file and
run git commit and git push.

root of repositories:

$HOME/repos
"""
from __future__ import print_function

import hashlib
import os
from os.path import abspath, relpath, dirname, isfile, join
import shutil
import subprocess as sp
import sys

def compute_hash(afile, blocksize=65536):
    """
    Compute the hex md5hash of a file.
    """
    with open(afile, 'rb') as fd:
        hasher = hashlib.md5()
        buf = fd.read(blocksize)
        while len(buf) > 0:
            # digest large files
            hasher.update(buf)
            buf = fd.read(blocksize)
    return hasher.hexdigest()


def compare_filehashes(afile, bfile):
    """
    Given the paths to two files, computes the md5 hash of these files.
    
    Returns
     - True if the files have the same md5 hash
     - False otherwise
    """
    h1 = compute_hash(afile)
    h2 = compute_hash(afile)
    if h1 == h2:
        return True
    else:
        return False
    


if __name__ == "__main__":
    
    root = join(os.environ["HOME"], "repos")
    for arg in sys.argv:
        if isfile(arg):
            # we are dealing with a file
            rel = relpath(arg, root)
            repo, fname = rel.split("/", 1)
            for r in os.listdir(root):
                # recurse through all repositories
                newrepo = join(root, r)
                newfile = join(newrepo, fname)
                arg = abspath(arg)
                newfile = abspath(newfile)
                if compare_filehashes(arg, newfile):
                    # the files are the same or 
                    continue
                if isfile(newfile):
                    # update the file in each repository
                    print("Copying {} to {}".format(arg, newfile))
                    shutil.copy2(arg, newfile)
                    print("Commit-Pushing")
                    os.chdir(newrepo)
                    try:
                        errorcode = sp.check_output("git commit -a -m 'update {} with {}'".format(fname, basename(__file__)), shell=True)
                        print("Commit returned:", errorcode)
                    except:
                        pass
                    finally:
                        sp.check_output("git push", shell=True)
                            
