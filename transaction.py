from eth_typing.evm import Address # nicht notwendig 
from web3 import Web3

ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

rpi1_address = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" #RPi 1 Address
rpi2_address = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" #RPi 2 Address


#TO DO: safe private key in python lib


private_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" #private key RPi 1

nonce= web3.eth.getTransactionCount(account_1)

#Create transaction
tx = {
'nonce': nonce,
'to': account_2,
'value': web3.toWei(0.005 , 'ether'),
'gas': 21000,
'gasPrice': web3.toWei('50', 'gwei') #how many gas we send in gwei
}

#RPi1 Address signs transaction
signed_tx = web3.eth.account.signTransaction(tx, private_key)

#want to get the transaction hash (not really necessary) but is a confirmation of transaction
tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction) 
print(web3.toHex(tx_hash)) 

#get the Balance of RPi1 
balance_rpi1 = web3.eth.getBalance(account_1)
conv_balance1 = web3.fromWei(balance_rpi1, 'ether') #convert to eth and print 
print(conv_balance1)

#get the Balance of RPi2
balance_rpi2 = web3.eth.getBalance(account_2)
conv_balance2 = web3.fromWei(balance_rpi2, 'ether') 
print(conv_balance2)



#trying to get Latest Transaction
"""
filter = web3.eth.get_filter_logs({
    'fromBlock': 0,
    'toBlock': 'latest',
    'address': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
})
"""

#event_filter = web3.eth.filter({"address": account_2, 'transactionHash':'0x6f4492c7384664fb43dffbec69afe643c3fd0d37ce5556a8de8c7e733038a3ac'})

#print(filter)


#print(dir(web3.eth))
