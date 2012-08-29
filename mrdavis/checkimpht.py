#!/usr/bin/env python

import sys

import numpy as np

import pyfits

class CheckImpht(object):
  """
  Perform checks on an IMPHTTAB produced by reftools.mkimphttab.createTable.
  The checks do not validate the data contained in the table, just check the
  table for internal consistency.
  
  Takes a pyfits.core.HDUList object as input.
  
  """
  def __init__(self,fits_obj):
    self.fits = fits_obj
    
    self.check_header_keys()
    self.read_header()
    
  def check_header_keys(self):
    """
    Check that the header has all the keywords we expect it to.
    
    """
    keys = ['SIMPLE',
             'BITPIX',
             'NAXIS',
             'EXTEND',
             'DATE',
             'FILENAME',
             'FILETYPE',
             'NEXTEND',
             'PHOTZPT',
             'PARNUM',
             'DBTABLE',
             'INSTRUME',
             'DETECTOR',
             'SYNSWVER',
             'MKTABVER',
             'GRAPHTAB',
             'COMPTAB',
             'USEAFTER',
             'PEDIGREE',
             'DESCRIP']
             
    for k in keys:
      if not self.fits['primary'].header.has_key(k):
        print 'Header does not have key {}'.format(k)
    
  def read_header(self):
    """
    Read in whatever header keywords we're interested in.
    
    """
    self.num_ext = self.fits['primary'].header['nextend']
    self.num_par = self.fits['primary'].header['parnum']
    
  def check_header_vals(self):
    """
    Check header keyword values say what they should say.
    
    """
    print '** Checking header values.'
    
    if self.num_ext != len(self.fits)-1:
      s = 'Number of image extensions is {} and does not match header keyword {}.'
      print s.format(len(self.fits)-1, self.num_ext)
      
  def check_ext_data(self):
    """
    Run all the tests that apply to an extension.
    
    """
    for i,ext in enumerate(self.fits[1:]):
      print '** Checking extension {}'.format(ext.name)
      
      # check that all the obsmodes start with the same string
      start = ext.data['obsmode'][0].strip().split(',')[0]
      
      if not np.char.startswith(ext.data['obsmode'],start).all():
        w = np.where(np.char.startswith(ext.data['obsmode'],start) != True)
        
        s = 'obsmode for row {}: {} does not match row 0:{}\n'
        
        for i in w[0]:
          print(s.format(i,ext.data['obsmode'][i],ext.data['obsmode'][0]))
      
      # perform other checks on individual rows
      self.check_rows(ext,i+1)
      
  def check_rows(self,ext,ext_num):
    """
    Run all the tests that apply to an extension row.
    
    """
    for i,row in enumerate(ext.data):
#      print '** Checking row {} of extension {}.'.format(i,ext.name)
      check_obsmode(row['obsmode'],ext_num,i)
      check_row_len(self.num_par,row,ext_num,i)
      check_row(self.num_par, row, ext_num, i)
      
  def run_checks(self):
    self.check_header_vals()
    self.check_ext_data()
      
def check_obsmode(obsmode,ext_num,row_num):
  """
  Is obsmode set to something?
  """
  
  if len(obsmode) == 0:
    print 'Obsmode column is empty for extension {} row {}'.format(ext_num,row_num)
    
def check_row_len(num_par,row,ext_num,row_num):
  """
  Does the row have the expected number of columns?
  """
  
  len_should = 5 + (4 * num_par)
  
  if len(row) != len_should:
    s = 'Row {} of extension {} should have length {} but has length {}'
    print s.format(row_num, ext_num, len_should, len(row))
    
def check_row(num_par,row,ext_num,row_num):
  """
  Does the column specified in the datacol column contain data, and do the
  other data columns contain zero? Also checks the paramter names, values,
  parameter number of elements columns.
  """
  
  datacol = row['datacol']
  
  if datacol[-1] not in [str(x) for x in range(1,num_par+1)]:
    # plain, single number case
    
    # check that the data column has a value
    if row['datacol'] == 0:
      s = 'Column {} of extension {} row {} is zero and shouldn\'t be.'
      print s.format(datacol, ext_num, row_num)
    
    # check that the other data columns are [0]
    datacolnum = ['{}{}'.format(datacol,x) for x in range(1,num_par+1)]
    
    for d in datacolnum:
      try:
        if row[d].tolist() != [0]:
          s = 'Column {} of extension {} row {} is not [0]. {} instead.'
          print s.format(d, ext_num, row_num, row[p])
      except AttributeError:
        s = 'Column {} of extension {} row {} is not an array. {} instead.'
        print s.format(p, ext_num, row_num, row[p])
        
    # check that the parameter names are ''
    parnames = ['PAR{}NAMES'.format(x) for x in range(1,num_par+1)]
    
    for p in parnames:
      if row[p] != '':
        s = 'Column {} of extension {} row {} has value {} when it should be blank.'
        print s.format(p, ext_num, row_num, row[p])
        
    # check that the parameter values are [0]
    parvals = ['PAR{}VALUES'.format(x) for x in range(1,num_par+1)]
    
    for p in parvals:
      try:
        if row[p].tolist() != [0]:
          s = 'Column {} of extension {} row {} is not [0]. {} instead.'
          print s.format(p, ext_num, row_num, row[p])
      except AttributeError:
        s = 'Column {} of extension {} row {} is not an array. {} instead.'
        print s.format(p, ext_num, row_num, row[p])
        
    # check that the nelem# keywords are 0
    nelems = ['NELEM{}'.format(x) for x in range(1,num_par+1)]
    
    for n in nelems:
      if row[n] != 0:
        s = 'Column {} of extension {} row {} is not 0. {} instead.'
        print s.format(n, ext_num, row_num, row[n])
    
  else:
    # one of the parameter sets that's stored as an array
    # (stuff here starts assuming that there are 9 or fewer parameters)
    # (i.e., they only take up one character space)
    
    # check that the plain data column is 0
    if row[datacol[:-1]] != 0:
      s = 'Column {} of extension {} row {} is not 0. {} instead.'
      print s.format(datacol[:-1], ext_num, row_num, row[datacol[:-1]])
      
    # how many parameters are we actually dealing with (must be <= num_par from header)
    np = int(datacol[-1])
    
    # the array length in datacol should be nelem1 * nelem2 * nelem3 *... up to
    # and including nelem#np
    # check array length and the values in the NELEM# columns up to nelem#np
    nelems = ['NELEM{}'.format(x) for x in range(1,np+1)]
    data_len = 1
    
    for n in nelems:
      if row[n] == 0:
        s = 'Column {} of extension {} row {} is zero and shouldn\'t be.'
        print s.format(n, ext_num, row_num)
      
      data_len *= row[n]
        
    if len(row[datacol]) != data_len:
      s = 'Column {} of extension {} row {} should have length {}. Has length {} instead.'
      print s.format(datacol, ext_num, row_num, data_len, len(row[datacol]))
      
    # check that the rest of the NELEM# fields are 0
    nelems = ['NELEM{}'.format(x) for x in range(np+1,num_par+1)]
    
    for n in nelems:
      if row[n] != 0:
        s = 'Column {} of extension {} row {} is not 0. {} instead.'
        print s.format(n, ext_num, row_num, row[n])
    
    # only the data column specified by datacol should be populated, all others
    # should be [0]
    datacolnum = ['{}{}'.format(datacol[:-1],x) for x in range(1,num_par+1)]
    datacolnum.remove(datacol)
    
    for d in datacolnum:
      try:
        if row[d].tolist() != [0]:
          s = 'Column {} of extension {} row {} is not [0]. {} instead.'
          print s.format(d, ext_num, row_num, row[p])
      except AttributeError:
        s = 'Column {} of extension {} row {} is not an array. {} instead.'
        print s.format(p, ext_num, row_num, row[p])
    
    
    # parameter columns up to and including the number of parameters np should
    # be populated, columns with parameter numbers higher should not be populated.
    # check that the parameter names are not '' up to par{#np}name
    parnames = ['PAR{}NAMES'.format(x) for x in range(1,np+1)]
    
    for p in parnames:
      if row[p] == '':
        s = 'Column {} of extension {} row {} is blank when it shouldn\'t be.'
        print s.format(p, ext_num, row_num)
        
    # check that the rest of them are ''
    parnames = ['PAR{}NAMES'.format(x) for x in range(np+1,num_par+1)]
    
    for p in parnames:
      if row[p] != '':
        s = 'Column {} of extension {} row {} has value {} when it should be blank.'
        print s.format(p, ext_num, row_num, row[p])
        
    # all par#value columns up to #np should have the length specified in 
    # the corresponding nelem# column
    parvals = ['PAR{}VALUES'.format(x) for x in range(1,np+1)]
    nelems = ['NELEM{}'.format(x) for x in range(1,np+1)]
    
    for p,n in zip(parvals,nelems):
      if len(row[p]) != row[n]:
        s = 'Length of column {} of extension {} row {} should be {}. {} instead.'
        print s.format(p, ext_num, row_num, row[n], len(row[p]))
        
    # all the rest of the par#values columns should be [0]
    parvals = ['PAR{}VALUES'.format(x) for x in range(np+1,num_par+1)]
    
    for p in parvals:
      try:
        if row[p].tolist() != [0]:
          s = 'Column {} of extension {} row {} is not [0]. {} instead.'
          print s.format(p, ext_num, row_num, row[p])
      except AttributeError:
        s = 'Column {} of extension {} row {} is not an array. {} instead.'
        print s.format(p, ext_num, row_num, row[p])

def usage():
  print 'Usage: checkimpht.py <impht fits table>'

if __name__ == '__main__':
  if len(sys.argv) != 2:
    usage()
    exit()
    
  print '** Running checks on file {}'.format(sys.argv[1])
    
  fits = pyfits.open(sys.argv[1],'readonly')
  
  checker = CheckImpht(fits)
  
  checker.run_checks()
  
  fits.close()
