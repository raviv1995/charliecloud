#!/usr/bin/env python3

# This script walks the directories specified in sys.argv[1:] prepared by
# make-perms-test.sh and attempts to read, write, and traverse (cd) each of
# the entries within. It compares the result to the expectation encoded in the
# filename.
#
# A summary line is printed on stdout. Running chatter describing each
# evaluation is printed on stderr.
#
# Note: This works more or less the same as an older version embodied by
# `examples/sandbox.py --filesystem` but is implemented in pure Python without
# shell commands. Thus, the whole script must be run as root if you want to
# see what root can do.

import os.path
import random
import re
import sys

EXPECTED_RE = re.compile(r'~(...)$')
class Makes_No_Sense(TypeError): pass

def main():
   dirs = sys.argv[1:]
   if (len(dirs) < 1):
       error('nothing to test')
   mismatch_ct = 0
   for d in dirs:
      for path in sorted(os.listdir(d)):
         mismatch_ct += not test('%s/%s' % (d, path))
   if (mismatch_ct == 0):
      print('SAFE\t', end='')
   else:
      print('RISK\t', end='')
   print('%d mismatches in %d directories' % (mismatch_ct, len(dirs)))

# Table of test function name fragments.
testvec = { (False, False, False): ('X', 'bad'),
            (False, False, True ): ('l', 'broken_symlink'),
            (False, True,  False): ('f', 'file'),
            (False, True,  True ): ('f', 'file'),
            (True,  False, False): ('d', 'dir'),
            (True,  False, True ): ('d', 'dir') }

def error(msg):
   print('ERROR\t%s' % msg)
   sys.exit(1)

def expected(path):
   m = EXPECTED_RE.search(path)
   if (m is None):
      return '*'
   else:
      return m.group(1)

def test(path):
   filetype = (os.path.isdir(path),
               os.path.isfile(path),
               os.path.islink(path))
   print('%s %-24s' % (testvec[filetype][0], path), file=sys.stderr, end='')
   expect = expected(path)
   result = ''
   for op in 'r', 'w', 't':  # read, write, traverse
      f = globals()['try_%s_%s' % (op, testvec[filetype][1])]
      try:
         f(path)
      except (PermissionError, Makes_No_Sense):
         result += '-'
      except Exception as x:
         error('exception on %s: %s' % (path, x))
      else:
         result += op
   print(' %s' % result, file=sys.stderr, end='')
   if (expect != '*' and result != expect):
      print(' mismatch', file=sys.stderr)
      return False
   else:
      print(' ok', file=sys.stderr)
      return True

def try_r_bad(path):
   error('bad file type: %s' % path)
try_t_bad = try_r_bad
try_w_bad = try_r_bad

def try_r_broken_symlink(path):
   raise Makes_No_Sense()
try_t_broken_symlink = try_r_broken_symlink
try_w_broken_symlink = try_r_broken_symlink

def try_r_dir(path):
   os.listdir(path)

def try_t_dir(path):
   try_r_file(path + '/file')

def try_w_dir(path):
   try_w_file('%s/a%d' % (path, random.getrandbits(64)))

def try_r_file(path):
   with open(path, 'rb', buffering=0) as fp:
      fp.read(1)

def try_t_file(path):
   raise Makes_No_Sense()

def try_w_file(path):
   # The file should exist, but this will create it if it doesn't. We don't
   # check for that error condition because we *only* want to touch the OS for
   # open(2) and write(2).
   with open(path, 'wb', buffering=0) as fp:
      fp.write(b'written by fs_test.py\n')

if (__name__ == '__main__'):
   main()
