import requests
from web3 import Web3
import json

# Evtll unterschiedliche Tokenamounts für average or current
BASE= "http://127.0.0.1:8030/" # rest api
rpi1_address = "0xD8a33Bc7c54F09F712C395F409819E8F40b59c57" #rpi 1 address

rpi1_privateKey = "b4cc69d2296a26a9d580116c3ae71dcb41932efeb35e2a347330ba0b4aa9955e" #-> env variable

# Connect web3 to Ganache node
ganache_url = "HTTP://127.0.0.1:7545" # ganache url
web3 = Web3(Web3.HTTPProvider(ganache_url))

gasLimit = 21000
#gasPrice = web3.toWei('40', 'gwei') # muss noch konvertiert werden
gasPrice =  web3.toWei(gasLimit, 'ether'),

gas =float('.'.join(str(elem) for elem in gasPrice))
print(gas)



# Request the transaction info to send tokens
response = requests.get(BASE + "helloworld/temperature")

# Get the headers of the response of rpi2 (transaction info)
rpi2_address = response.headers['X-rpi2Address']
tokenAmount =  response.headers['X-tokenAmount']
#print(response.json())

# TEST:
print(rpi2_address)
print(tokenAmount)

# Method to request the current balance
def getBalance(address):
    balance = web3.eth.getBalance(address)
    balance_conv = web3.fromWei(balance, 'ether') # ether 18 decimals convert balance
    return balance_conv

# TEST:
currBalance = getBalance(rpi1_address)
print(currBalance)

# Method to verify the transaction
def verifyTransaction(address_rpi2, address_rpi1, amount):
    balanceRpi1 = getBalance(address_rpi1) # Get current balance of rpi1
    # Check if the balance of rpi1 is enough <= (token + gasPrice)
    if(float(balanceRpi1) < (float(amount) + 0.00000002)): #gasPrice konvertieren (vllt estimated gaslimtit??)
        return "Not enough tokens for transaction. Please buy more token."
    else:
        tx = createTx(address_rpi2, amount, address_rpi1)
        return tx

# Create the transaction and return the created tx
def createTx(address_rpi2, amount, address_rpi1):
    nonce= web3.eth.getTransactionCount(address_rpi1)

    tx = {
    'nonce': nonce,
    'to': address_rpi2,
    'value': web3.toWei(amount, 'ether'),
    'gas': 21000, # max amount of gas price you are willing to pay for tx
    'gasPrice': web3.toWei('40', 'gwei'), # gasprice we actually send to send tx
}
    return tx

created_tx = verifyTransaction(rpi2_address, rpi1_address, tokenAmount)

# Sign the transaction with private key of rpi1
def signTransaction(tx, privateKey):
    signed_tx = web3.eth.account.signTransaction(tx, privateKey)
    return signed_tx

signed_tx = signTransaction(created_tx, rpi1_privateKey)

# Hashkey is a confirmation of a successful transaction
# Method sends transaction and returns the hashKey
def sendTxgetHash(signed_tx):
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    hash = web3.toHex(tx_hash) #evtll noch in einzelne Methoden auslagern
    return hash

transactionHash = sendTxgetHash(signed_tx)
#txnInfo= web3.eth.getTransaction(transactionHash)
#print(txnInfo)

# TEST
print(transactionHash)

# make a request at endpoint '/data' and send the transactionHash through headers
# the programmcode of rpi2 verifies the transaction and sends data


#Send the transactionHash and address of RPi1 through a header
custom_headers= {'X-transactionHash': transactionHash, 'X-rpi1Address': rpi1_address}
data_request = requests.get(BASE + "data", headers=custom_headers)

temp_dict = data_request.json()
currTemp = temp_dict['temperature']
print(str(currTemp)+" °C")


#Access body to get sensordata (?)
#x = respi.request.body
#print(x)


#-----------trying to post sth------- NOT NEEDED:
#payload = transactionHash
#send = requests.post(BASE, payload)
#------------------------------------

#respo = requests.get(BASE + "data")

