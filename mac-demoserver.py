# -*- coding: utf-8 -*-
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
	s.bind(('192.168.1.81', PORT))
	plt.figure(figsize=(4, 2), dpi=200)  # 縦横サイズと解像度を指定
	#plt.subplots_adjust(wspace=0.4, hspace=0.45)
	ax = plt.subplot(111)
	#rcParams['figure.figsize'] = 10,10
	while (1):
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
			elif(len(xpoint) == 50) :
				for i in range(49) :
					xpoint[i] = xpoint[i+1]
					ypoint[i] = ypoint[i+1]
				xpoint[49] = datalist[0]
				ypoint[49] = datalist[1]
			lines = ax.plot(xpoint, ypoint,color="k",linewidth=0.5)
			#lines.set_data(xpoint, ypoint)
			ax.set_xlim((float(xpoint[0]), float(xpoint[0])+10))
			ax.set_ylim((0, 1024))

			plt.pause(0.01)
			plt.cla()
			#time.sleep(0.05)
		finally:
			connection.close()