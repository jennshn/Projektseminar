#import json
from flask import Flask, request, redirect
from flask.helpers import make_response
import requests
#from influxdb import InfluxDBClient
#import jsonify
from flask_restful import Api, Resource, reqparse
from web3 import Web3
from time import sleep # error cuz to many requests sleep(seconds)
from requests.exceptions import ConnectionError # handle connection error

# in env variablen (damit es nicht in url ersichtlich ist)


# Build a REST api for Raspberry Pi 2, so rpi2 can handle specific requests
# Hinzufügen: Statuscodes
app = Flask(__name__)
api = Api(app)

# Sensitive Data
user = "prosem"
password = "prosem21kp"


#data_request_args = reqparse.RequestParser()
#data_request_args.add_argument('text', location = ['headers']) #not case-sensitive anymore


# Connect web3 to the Ganache node
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Endpoint to request sensordata from raspberry pi2
sensor_url = "http://132.199.123.229:54683/query" #Better url building!!

address_rpi2 = "0x1Abb50561Ef7b74594C2254293DB332712fdDca7" # rpi2 wallet address
tokenAmount = 0.03

# To verify the transaction of rpi1 we need to get the balance of rpi2 (so we can send sensordata)
def getBalance(address):
    balance = web3.eth.getBalance(address)
    balance_conv = web3.fromWei(balance, 'ether') # ether 18 decimals convert balance
    return balance_conv

balance_rpi2 = getBalance(address_rpi2) #NEW

# Create a Resource to handle requests and return the transaction info: rpi2 address and token amount
class Transaction_Info(Resource):
    def get(self, req_value):
        #global balance_rpi2
        if(req_value == "temperature" or "humidity"):
            response = make_response()
            response.headers['X-rpi2Address'] = address_rpi2
            response.headers['X-tokenAmount'] = tokenAmount
            #balance_rpi2 = getBalance(address_rpi2) # Every time there is a request, getbalance
        return response
        # need to return something serializable --> python dict i.e. (json serializable)

# Add the Resource Transaction Info to our REST Api
api.add_resource(Transaction_Info, '/helloworld/<string:req_value>')

print(balance_rpi2)

# Handles the data request after the transaction
class Data_Request(Resource):
    def get(self):
        global balance_rpi2
        currBalance = getBalance(address_rpi2)
        txnInfo_rpi1 = request.headers['X-transactionHash'] #get the headers of rpi1 get request
        address_rpi1 = request.headers['X-rpi1Address']
        txnInfo= web3.eth.getTransaction(txnInfo_rpi1) #überprüfen ob es überhaupt ein valider Hash ist fehlt!!!
        hash_from = txnInfo.get('from')
        hash_to = txnInfo.get('to')

        if(float(currBalance) >= (float(balance_rpi2) + float(tokenAmount))):
            #print(currBalance)
            if((hash_to == address_rpi2) and (hash_from == address_rpi1)):
                balance_rpi2 = currBalance # Update the balance variable
                return redirect('/temperature/current')
        else:
            return print("Not enough token sent!")


# Add the Resource Data Request to our REST Api
api.add_resource(Data_Request, '/data', endpoint="data")

balance_rpi2 = getBalance(address_rpi2)

# Following get requests are fetching sensor_data of rpi2: (Data: current temperature and humidity, mean temperature and humidity)
@app.route("/temperature/current", methods = ['GET'])
def get_temperature():
    i=0
    while i <30:
        try:
            url_params={'pretty': True, 'db':'sensor_data', 'q':'SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 30m'}
            r = requests.get(sensor_url, auth=(user, password), params=url_params).json()
            currentTemp = r['results'][0]['series'][0]['values'][-1][1] #get the current temperature without time
            return {'temperature': currentTemp}

        except requests.ConnectionError:
            sleep(1)
            i+=1
            return print("Not found")

@app.route("/humidity/current", methods= ['GET'])
def get_humidity():
    try:
        url_params = {'pretty': True, 'db':'sensor_data', 'q':'SELECT \"humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 30m'}
        h = requests.get(sensor_url, auth=(user, password), params=url_params).json()
        currentHumidity = h['results'][0]['series'][0]['values'][-1][1] #get the current humidity
        return {'temperature': currentHumidity}

    except requests.ConnectionError:
        return print("Not found")

@app.route("/temperature/average", methods =['GET'])
def get_tempMean():
    h = requests.get(sensor_url, auth=(user, password), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT mean(\"temperature\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'}).json()
    currentTempMean = h['results'][0]['series'][0]['values'][-1][1] #get the temp average of today
    return str(round(currentTempMean, 2))+" °C"

@app.route("/humidity/average", methods =['GET'])
def get_humidityMean():
    try:
        url_params = {'pretty': True, 'db':'sensor_data', 'q':'SELECT mean(\"humidity\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'}
        h = requests.get(sensor_url, auth=(user, password), params=url_params).json()
        humidityMean = h['results'][0]['series'][0]['values'][-1][1] #get the hum average of today
        return {'temperature': round(humidityMean, 2)}

    except requests.ConnectionError:
        return print("Not found")

if __name__ == '__main__':
    app.run(port=8030, debug =True) # Run the app on localhost:8030
    #Am Ende debug auf false setzen