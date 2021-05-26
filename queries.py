import jsonify, requests 
from influxdb import InfluxDBClient
import datetime #jsonify and datetime NOT needed for code

client=InfluxDBClient(host='132.199.123.229', port=54683, username='prosem', password='prosem21kp', database='sensor_data')

results = client.query('SELECT \"temperature\" FROM \"sensor_data\".\"autogen\".\"mqtt_consumer\" WHERE \"time\" > now() - 1d', method='GET')

print(results)

#print(results.raw)
