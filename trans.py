from eth_typing.evm import Address
from influxdb import resultset
from web3 import Web3

ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

account_1 = "0x2F74924f033cB4e8Cb44f78B3599CEFF3DaD6477" #RPi 1 Address
account_2 = "0xF5d4243c6e8262f126a7E24084f0c352bb74982d" #RPi 2 Address

private_key = "a3202f3ff16437c9b19eb2ed870b1d3e0f5a2760dc3ebc183e390e73177fc87b" #private Key RPi 1

nonce= web3.eth.getTransactionCount(account_1)

#transaction
tx = {
'nonce': nonce,
'to': account_2,
'value': web3.toWei(0.01, 'ether'),
'gas': 21000,
'gasPrice': web3.toWei('50', 'gwei') #how many gas we send in gwei
}

#sign transaction
signed_tx = web3.eth.account.signTransaction(tx, private_key)

#want to get the transaction hash (not really necessary) but is a confirmation of transaction
tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction) 
print(web3.toHex(tx_hash)) 

balance_pi1 = web3.eth.getBalance(account_1)
conv_balance = web3.fromWei(balance_pi1, 'ether')
print(conv_balance)


filter = web3.eth.get_filter_logs({
    'fromBlock': 0,
    'toBlock': 'latest',
    'address': '0x2F74924f033cB4e8Cb44f78B3599CEFF3DaD6477',
})


event_filter = web3.eth.filter({"address": account_2, 'transactionHash':'0x6f4492c7384664fb43dffbec69afe643c3fd0d37ce5556a8de8c7e733038a3ac'})

print(filter)


#print(dir(web3.eth))
