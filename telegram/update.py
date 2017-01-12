import zmq
import random
import sys
import time
import json

port = "5555"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

with open('../houses.json') as houses_file:
	houses = json.load(houses_file)
	for house in houses:
		print("Sending house {}".format(house['id']))
		socket.send_string(json.dumps(house))
