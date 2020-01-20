from __future__ import unicode_literals, print_function
from pylab import rcParams
import socket
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

PORT = 50000
BUFFER_SIZE = 1024
start = time.time()
xpoint = []
ypoint = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind(('192.168.1.33', PORT))
	fig, ax = plt.subplots(1, 1)
	#rcParams['figure.figsize'] = 10,10
	while (time.time()-start <= 30):
		s.listen()
		(connection, client) = s.accept()
		try:
			print('Client connected', client)
			data = connection.recv(BUFFER_SIZE)
			comment = "reserved "
			#connection.send(comment.encode())
			dataline = data.decode()
			datalist = dataline.split()
			datalist[0] = float(datalist[0])
			datalist[1] = float(datalist[1])
			print("time: " + str(datalist[0]))
			print("data: " + str(datalist[1]))


			if(len(xpoint) <= 49) :
				xpoint.append(datalist[0])
				ypoint.append(datalist[1])
			else :
				for i in range(49) :
					xpoint[i] = xpoint[i+1]
					xpoint[49] = datalist[0]
					ypoint[i] = ypoint[i+1]
					ypoint[49] = datalist[1]
			lines = ax.plot(xpoint, ypoint)
			#lines.set_data(xpoint, ypoint)
			ax.set_xlim((float(xpoint[0]), float(xpoint[0])+10))
			ax.set_ylim((0, 1024))
			plt.pause(0.01)
		finally:
			connection.close()