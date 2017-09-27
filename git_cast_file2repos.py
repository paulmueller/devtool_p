#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copy a file to all directories on same level that contain same file and
run git commit and git push.

root of repositories:
    
    $HOME/repos


Example usage:

    # Update all all checked-out repositories under "repos" with "_version.py"
    python git_cast_file2repos.py --replace_name /home/paul/repos/nrefocus/nrefocus/_version.py
    


Command line arguments:

    --replace_name
        Add this if you would like to replace all occurences of the repository
        name in the path. E.g. if you want to copy
        
        /home/user/repos/Foo/foo/version.py -> /home/user/repos/Bar/bar/version.py
        
        By default, only this would work:
        /home/user/repos/Foo/foo/version.py -> /home/user/repos/Bar/foo/version.py
"""
from __future__ import print_function

import hashlib
import os
from os.path import abspath, relpath, isfile, join, basename
import shutil
import subprocess as sp
import sys
import traceback

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
    h2 = compute_hash(bfile)
    return h1 == h2
    

if __name__ == "__main__":
    
    root = join(os.environ["HOME"], "repos")

    replace_name = sys.argv.count("--replace_name")
    
    for arg in sys.argv[1:]:
        if isfile(arg):
            # we are dealing with a file
            rel = relpath(arg, root)
            repo, fname = rel.split("/", 1)
            for r in os.listdir(root):
                # recurse through all repositories
                newrepo = join(root, r)
                if replace_name:
                    _oldreponame = basename(repo).lower()
                    _newreponame = basename(newrepo).lower()
                    fname2 = fname.replace(_oldreponame, _newreponame)
                else:
                    fname2 = fname
                newfile = join(newrepo, fname2)
                arg = abspath(arg)
                newfile = abspath(newfile)
                if isfile(newfile):
                    if compare_filehashes(arg, newfile):
                        # the files are the same or
                        continue
                    # update the file in each repository
                    print("Copying {} to {}".format(arg, newfile))
                    shutil.copy2(arg, newfile)
                    print("Commit-Pushing")
                    os.chdir(newrepo)
                    try:
                        errorcode = sp.check_output("git commit -a -m 'update {} with {}'".format(fname2, basename(__file__)), shell=True)
                        print("Commit returned:", errorcode)
                        sp.check_output("git push", shell=True)
                    except:
                        print(traceback.format_exc())
                        
                            
