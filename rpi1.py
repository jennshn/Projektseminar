from flask import Flask, request
from flask.helpers import make_response
import requests
from flask_restful import Api, Resource
from web3 import Web3
from time import sleep
from requests.exceptions import ConnectionError
import os

app = Flask(__name__)
api = Api(app)

# Access data to the database
user = os.environ.get('RPI2_USER') #CHANGE TO DB_USER AND DB_PASSWORD
password = os.environ.get('RPI2_PASSWORD')

# Connect web3 to the Rinkeby Network
infura_url = "https://rinkeby.infura.io/v3/3423f6258c3b46e98459616f589e4300"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Endpoint of the influx database of pi 1
sensor_url = "http://132.199.123.229:54683/query"

rpi1_address = "0x839a21ccdF3c54EA69C2eAAd942073568172cCE9"
tokenAmount = 0.0001

# Get the current balance of the passed address
def getBalance(address):
    balance = web3.eth.getBalance(address)
    convertedBalance = web3.fromWei(balance, 'ether')
    return convertedBalance

# Get current balance
rpi1_balance = getBalance(rpi1_address)

# Method checks the passed arguments when a client trys to access the SensorData resource
def requestedMeasurement(measurement, measurementType):
    if(measurement == 'temperature' and measurementType == "current"):
        temp = getTempSeries()
        value = temp[-1] # Last value of temperature series to get the current temperature
    elif(measurement == 'humidity' and measurementType == "current"):
        humidity = getHumiditySeries()
        value = humidity[-1] # Last value of humidity series to get the current humidity
    elif(measurement == 'temperature' and measurementType == "average"):
        value = getTemperatureMean()
    elif(measurement == 'humidity' and measurementType == "average"):
        value = getHumidityMean()
    elif(measurement == 'temperature' and measurementType == "series"):
        value = getTempSeries()
    elif(measurement == 'humidity' and measurementType == "series"):
        value = getHumiditySeries()

    # Returns the respective measurement in JSON format
    jsonResponse = {'value': str(value)}
    return jsonResponse

# Checks if an address is an eth address
def isValidAddress(address):
    isValid = Web3.isAddress(address)
    return isValid

# Verify the transaction of client
def verifyTransaction(addressFrom, addressTo, transactionFrom, transactionTo, currentBalance, balanceBefore, tokenAmount):
    if (float(currentBalance) >= (float(balanceBefore) + float(tokenAmount))
        and (transactionTo == addressTo)
        and (transactionFrom == addressFrom)):
        return True

# Get the average temperature of today
def getTemperatureMean():
    try:
        query = 'SELECT mean(\"temperature\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'
        url_params = {'pretty': True, 'db':'sensor_data', 'q':query}

        # Send a GET-request to the endpoint of influxDB with a query and basic auth
        h = requests.get(sensor_url, auth=(user, password), params=url_params).json()
        tempMeanToday = h['results'][0]['series'][0]['values'][-1]
        return tempMeanToday

    except requests.ConnectionError:
        return print("Not found")

# Get the average humidty of today
def getHumidityMean():
    try:
        query = 'SELECT mean(\"humidity\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'
        url_params = {'pretty': True, 'db':'sensor_data', 'q':query}
        h = requests.get(sensor_url, auth=(user, password), params=url_params).json()
        humidityMeanToday = h['results'][0]['series'][0]['values'][-1]
        return humidityMeanToday

    except requests.ConnectionError:
        return print("Not found")

# Get a series of temperature values
def getHumiditySeries():
    try:
        query = 'SELECT \"humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 2h'
        url_params = {'pretty': True, 'db':'sensor_data', 'q':query}
        h = requests.get(sensor_url, auth=(user, password), params=url_params).json()
        humiditySeriesToday = h['results'][0]['series'][0]['values']
        return humiditySeriesToday

    except requests.ConnectionError:
        return print("Not found")


# Get a series of temperature values
def getTempSeries():
    try:
        query = 'SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() -2h'
        url_params = {'pretty': True, 'db':'sensor_data', 'q':query}
        h = requests.get(sensor_url, auth=(user, password), params=url_params).json()
        tempSeriesToday = h['results'][0]['series'][0]['values'] #[1]-> um ohne Zeitstempel #get the hum average of today
        #return str(round(humidityMeanToday, 2))+" %"
        return tempSeriesToday

    except requests.ConnectionError:
        return print("Not found")

# Creates a route that lists all available routes and ressources in JSON-format
@app.route('/')
def routes():
   routes = []
   for route in app.url_map.iter_rules():
    routes.append('%s' % route)
   return{'routes': routes}

# Resource to process incoming requests and return the transaction details
class TransactionData(Resource):
    def get(self):
        transactionInfo = {"rpi1_address": rpi1_address, "tokenAmount": tokenAmount}
        return transactionInfo

# Create an endpoint for the resource at /transaction/data
api.add_resource(TransactionData, '/transaction/data')

# Resource for the sensor data
class SensorData(Resource):
    def get(self, measurement, type):
        global key
        global rpi1_balance

        # Set a timer for 15-20 seconds to make sure that the token are in the wallet and balance is updated
        sleep(20)

        currentBalance = getBalance(rpi1_address)

        # Get the passed arguments of the request
        rpi2_address = request.args['rpi2_address']
        transactionHash = request.args['transactionHash']

        hashInfo = web3.eth.getTransaction(transactionHash)
        txFrom = hashInfo.get('from')
        txTo = hashInfo.get('to')

        if(isValidAddress(rpi1_address) == False):
            return "Invalid address!"

        # Verifies the transaction with passed arguments of the request
        if(verifyTransaction(rpi2_address, rpi1_address, txFrom, txTo, currentBalance, rpi1_balance, tokenAmount)):

            # Update the balance and return the requested sensor data
            rpi1_balance = currentBalance
            measurementResponse = requestedMeasurement(measurement, type)
            return make_response(measurementResponse)

        else:
            return print("Not enough token sent. Try again!")

api.add_resource(SensorData, '/data/<string:type>/<string:measurement>/', endpoint="data")

if __name__ == '__main__':
    app.run(port=8030, debug =False)