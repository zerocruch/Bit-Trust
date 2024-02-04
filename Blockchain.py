from datetime import datetime
import hashlib

class Blockchain:
	def __init__(self):
		self.__nonceXs = 2
		self.__Blockchain = [{
			'blockID' : 0,
			'nonce' : 417 ,
			'timestamp' : 0,
			'TransactionData' : {
				'From' : '_',
				'To' : 'ZEROCRUCH',
				'Ammount' : 99999999999
			},
			'PreviusBlockHash' : '00xZEROCRUCH'
		}]
	
	def ShowBlockchain(self) -> list:
		return self.__Blockchain
	
	def isValidHash(self, hash:str) -> bool:
		return hash.startswith(self.__nonceXs * '0')

	
	def CreateBlock(self, FromAddress:str, ToAddress:str, Ammount:float) -> bool:
		if self.AccountBalance(FromAddress) >= Ammount and ToAddress != FromAddress:
			try:
				previusBlock = self.__Blockchain[-1]
				blockID = previusBlock['blockID'] + 1
				timestamp = datetime.now().timestamp()
				previusBlockHash = hashlib.sha256(str(previusBlock).encode('utf-8')).hexdigest()
				NewBlock = {
						'blockID' : blockID,
						'nonce' : 0,
						'timestamp' : timestamp,
						'TransactionData' : {
							'From' : str(FromAddress),
							'To' : str(ToAddress),
							'Ammount' : Ammount
						},
						'PreviusBlockHash' : previusBlockHash
					}
				while True:
					if self.isValidHash(hashlib.sha256(str(NewBlock).encode('utf-8')).hexdigest()):
						return self.AddBlock(NewBlock)
					else:
						NewBlock['nonce'] += 1
			except Exception:
				return False
		else:
			return False
	
	def AddBlock(self, Block:dict) -> bool:
		self.__Blockchain.append(Block)
		return True
	
	def AccountBalance(self, accountAddress:str) -> float:
		accountBalnce = 0
		for block in self.__Blockchain:
			if block['TransactionData']['From'] == accountAddress:
				accountBalnce -= block['TransactionData']['Ammount']
			elif block['TransactionData']['To'] == accountAddress:
				accountBalnce += block['TransactionData']['Ammount']
		return accountBalnce



		