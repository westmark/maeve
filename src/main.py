#-*- coding: UTF-8 -*-

from maeve.api import *

if __name__ == '__main__':
  api = Api(867321, '9UW7DvM26ZRee5Go2ReWaIRJjCNWIXMJOO2vv1Jk1sL1LOig1BVTVrlBrcOrWIMB')
  api.authenticate()

  cid = '1714148081'

  char = api.get_character(cid)

  trans = char.WalletTransactions(rowCount=100)
  #sold_tx = trans.transactions.GroupedBy('transactionType')['sell']
  tx = trans.transactions#.SortBy('transactionID')
  ids = [row.transactionID for row in tx]

  print '\n'.join([str(id) for id in sorted(ids)])
  #for row in tx:
  #  print type(row.transactionID), row.transactionDateTime, row.transactionID, row.transactionType



  #char = get_character(auth, char_id)
  #get_buy_transactions_for(auth, char, '')

