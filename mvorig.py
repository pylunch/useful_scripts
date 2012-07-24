#!/usr/bin/env python
"""
Move input files to have suffix .orig.

Usage: mvorig.py <input files>

"""

import os.path
import sys
import shutil

def mvorig(files):
  for f in files:
    if os.path.exists(f):
      print('Moving file ' + f + ' to ' + f + '.orig')
      shutil.move(f,f+'.orig')
    else:
      print('File does not exist: ' + f)
    
def usage():
  print('mvorig.py <input files>')
  
if __name__ == '__main__':
  
  if len(sys.argv) < 2:
    usage()
    exit()
    
  mvorig(sys.argv[1:])
