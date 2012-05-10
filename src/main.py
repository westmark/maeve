#-*- coding: UTF-8 -*-

from maeve.api import *

if __name__ == '__main__':
  auth = get_auth(867321, '9UW7DvM26ZRee5Go2ReWaIRJjCNWIXMJOO2vv1Jk1sL1LOig1BVTVrlBrcOrWIMB')
  print auth.account.parameters
  char_id = '1714148081'

  #char = get_character(auth, char_id)
  #get_buy_transactions_for(auth, char, '')

