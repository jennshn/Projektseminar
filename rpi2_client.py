import requests
from web3 import Web3
import os

rpi1_url= "http://132.199.123.229:8030/"

# Acess private key from environment variable in pi 2
rpi2_privateKey = os.environ.get('RPI2_PRIVATEKEY')
rpi2_address = "0xD793b7d81B580b66E5934B95fA0cc3965e3c505F"

# Connect web3 to the Rinkeby network
infura_url = "https://rinkeby.infura.io/v3/3423f6258c3b46e98459616f589e4300"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Recommended gas for the fastest transaction
gas = 23
gasValue = web3.fromWei(gas, 'ether')

# Get the current balance of the passed address
def getBalance(address):
    balance = web3.eth.getBalance(address)
    convertedBalance = web3.fromWei(balance, 'ether')
    return convertedBalance


# Method to verify the balance
def verifyBalance(rpi1_address, rpi2_address, tokenAmount):
    currentBalance = getBalance(rpi2_address)
    if(float(currentBalance) < (float(tokenAmount) + float(gasValue))):
        return "Not enough tokens for transaction. Please buy more token."
    else:
        # If enough token are available create a transaction
        tx = createTx(rpi1_address, tokenAmount, rpi2_address)
        return tx

# Create a transaction with passed parameters and returns a created tx which needs to be signed
def createTx(rpi1_address, tokenAmount, rpi2_address):
    nonce= web3.eth.getTransactionCount(rpi2_address)

    tx = {
    'nonce': nonce,
    'to': rpi1_address,
    'value': web3.toWei(tokenAmount, 'ether'),
    'gas': 50000,
    'gasPrice': web3.toWei(gas, 'gwei'),
}
    return tx

# Sign the created transaction with a private key
def signTransaction(tx, privateKey):
    signedTx = web3.eth.account.signTransaction(tx, privateKey)
    return signedTx

# Method sends the signed transaction
def sendTx(signedTx):
    sentTx = web3.eth.sendRawTransaction(signedTx.rawTransaction)
    return sentTx

# Returns hashkey of sent transaction which is a confirmation of successful transaction
def getTransactionHash(sentTx):
    hashKey = web3.toHex(sentTx)
    return hashKey

# Send a GET-request to get the transaction info from pi 1
response = requests.get(rpi1_url + "transaction/data")

# Get the body of the response of pi 1
transactionInfo = response.json()
rpi1_address = str(transactionInfo['rpi1_address'])
tokenAmount =  str(transactionInfo['tokenAmount'])

# Initiate the transaction with received address of pi 1 and token amount
createdTx = verifyBalance(rpi1_address, rpi2_address, tokenAmount)
signedTx = signTransaction(createdTx, rpi2_privateKey)
sentTx = sendTx(signedTx)
transactionHash = getTransactionHash(sentTx)

print(transactionHash)

# Send the transactionHash and address of pi 2 as params
request_params= {'transactionHash': transactionHash, 'rpi2_address': rpi2_address}

# Send a GET-request to the endpoint data/current/humidity to get the current humdity
dataRequest = requests.get(rpi1_url + "data/current/humidity", params=request_params)

# Get the response body of to get the current humidity
responseValues = dataRequest.json()
value = responseValues['value']
print(value)
