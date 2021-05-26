import json
from flask import Flask, request
import requests
from influxdb import InfluxDBClient
#from flask_marshmallow import Marshmallow

app = Flask(__name__)
#ma = Marshmallow(app)


@app.route("/temperature", methods = ['GET'])
def get_temperature():
    r = requests.get('http://132.199.123.229:54683/query', auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'})
    return r

@app.route("/humidity", methods= ['GET'])
def get_humidity():
    h = requests.get('http://132.199.123.229:54683/query', auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT mean(\"humidity\") AS \"mean_humidity\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'})
    return h

if __name__ == '__main__':
    app.run(port=8030, debug =True)