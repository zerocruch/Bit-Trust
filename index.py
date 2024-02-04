import hashlib
from Blockchain import Blockchain




BlockchainData = Blockchain()

#print(BlockchainData.ShowBlockchain())
print(BlockchainData.CreateBlock('0', '1', 1))
print(BlockchainData.CreateBlock('ZEROCRUCH', '0', 1))
#print(BlockchainData.ShowBlockchain())
print(BlockchainData.CreateBlock('0', '1', 1))

print(BlockchainData.AccountBalance('0'))
print(BlockchainData.CreateBlock('0', '1', 1))
print(BlockchainData.CreateBlock('1', '0', 1))
print(BlockchainData.ShowBlockchain())