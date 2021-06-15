import json
from flask import Flask, request, redirect
from flask.helpers import make_response
import requests
from influxdb import InfluxDBClient
import jsonify
from flask_restful import Api, Resource
from web3 import Web3

# Build a REST api for Raspberry Pi 2, so rpi2 can handle specific requests
# Hinzufügen: Statuscodes
app = Flask(__name__)
api = Api(app)

# Connect web3 to the Ganache node
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Endpoint to request sensordata from raspberry pi2
sensor_url = "http://132.199.123.229:54683/query"

address_rpi2 = "0x1Abb50561Ef7b74594C2254293DB332712fdDca7" # rpi2 wallet address
tokenAmount = 0.03


# Not needed:
values = {"temperature": {"tokenAmount": tokenAmount, "account": address_rpi2},
          "humidity": {"tokenAmount": tokenAmount, "account": address_rpi2},
        }

# Create a Resource to handle requests and return the transaction info: rpi2 address and token amount
class Transaction_Info(Resource):
    def get(self, req_value):
        if(req_value == "temperature" or "humidity"):
            response = make_response()
            response.headers['X-rpi2Address'] = address_rpi2
            response.headers['X-tokenAmount'] = tokenAmount
        return response, 200
        # need to return something serializable --> python dict i.e. (json serializable)

# Add the Resource Transaction Info to our REST Api
api.add_resource(Transaction_Info, '/helloworld/<string:req_value>')

# To verify the transaction of rpi1 we need to get the balance of rpi2 (so we can send sensordata)
def getBalance(address):
    balance = web3.eth.getBalance(address)
    balance_conv = web3.fromWei(balance, 'ether') # ether 18 decimals convert balance
    return balance_conv


# Handles the data request after the transaction
class Data_Request(Resource):
    def get(self):
        currBalance = getBalance(address_rpi2)
        rpi1_transaction = request.headers['X-transactionHash'] #get the headers of rpi1 get request
        address_rpi1 = request.headers['X-rpi1Address']
        print(rpi1_transaction)
        print(address_rpi1)
        return redirect('/temperature/current') # <- noch nicht fertig
        # TO DO: get Balance and latest Transaction of rpi2

# Add the Resource Data Request to our REST Api
api.add_resource(Data_Request, '/data', endpoint="data")

###########
# TO DO: send the data to rpi1
#if((balance + tokenAmountOf) == currnetBalance):

# Not needed:
@app.route("/", methods=['POST'])
def data_request():
    if(request.method == 'POST'):
        data = request.get_json()
        return jsonify({'Your hash:': data}), 201
    else:
        return jsonify({'Send me': '20 Token!'})


#Following methods are fetching sensor_data of rpi1

@app.route("/temperature/current", methods = ['GET'])
def get_temperature():
    r = requests.get(sensor_url, auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 30m'}).json()
    currentTemp = r['results'][0]['series'][0]['values'][-1][1] #get the current temperature without time
    return str(currentTemp) +" °C"


@app.route("/humidity/current", methods= ['GET'])
def get_humidity():
    h = requests.get(sensor_url, auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT \"humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 30m'}).json()
    currentHumidity = h['results'][0]['series'][0]['values'][-1][1] #get the current humidity
    return str(currentHumidity)+" %"


@app.route("/temperature/average", methods =['GET'])
def get_humSeries():
    h = requests.get(sensor_url, auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT mean(\"temperature\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'}).json()
    currentTempSeries = h['results'][0]['series'][0]['values'][-1][1] #get the temp average of today
    return str(round(currentTempSeries,2))+" °C"

@app.route("/humidity/average", methods =['GET'])
def get_tempSeries():
    h = requests.get(sensor_url, auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT mean(\"humidity\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'}).json()
    currentHumiditySeries = h['results'][0]['series'][0]['values'][-1][1] #get the hum average of today
    return str(round(currentHumiditySeries,2))+" %"

if __name__ == '__main__':
    app.run(port=8030, debug =True) # Run the app on localhost:8030