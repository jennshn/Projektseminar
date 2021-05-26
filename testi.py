import json
from flask import Flask, request
import requests
from influxdb import InfluxDBClient

api_endpunkt = 'http://132.199.123.229:54683/query'
results = requests.get(api_endpunkt, auth=('prosem', 'prosem21kp'), params={'pretty': True, 'db':'sensor_data', 'q':'SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'})
#print(r.ok) #geht nicht
js = results.json()

print(js)

api_current_temp = str(js['results']['values'])

print(api_current_temp)
#r = requests.get('http://132.199.123.229:54683', auth=('prosem', 'prosem21kp'), params={'db':'sensor_data', 'q':'SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d'})
