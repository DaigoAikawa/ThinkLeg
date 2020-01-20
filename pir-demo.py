# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime
import socket

PORT = 50000
BUFFER_SIZE = 1024

GPIO.setwarnings(False)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
	if adcnum > 7 or adcnum < 0:
		return -1

	GPIO.output(cspin, GPIO.HIGH)
	GPIO.output(clockpin, GPIO.LOW)
	GPIO.output(cspin, GPIO.LOW)

	commandout = adcnum
	commandout |= 0x18 #スタートビット+シングルエンドビット
	commandout <<= 3 #LSBから8ビット目を送信するようにする

	for i in range(5):
		if commandout & 0x80:
			GPIO.output(mosipin, GPIO.HIGH)
		else:
			GPIO.output(mosipin, GPIO.LOW)
		commandout <<= 1
		GPIO.output(clockpin, GPIO.HIGH)
		GPIO.output(clockpin, GPIO.LOW)

	adcout = 0

         #11ビット読む
	for i in range(11):
		GPIO.output(clockpin, GPIO.HIGH)
		GPIO.output(clockpin, GPIO.LOW)
		adcout <<= 1
		if i>0 and GPIO.input(misopin)==GPIO.HIGH:
			adcout |= 0x1
	GPIO.output(cspin, GPIO.HIGH)
	return adcout
GPIO.setmode(GPIO.BCM)
SPICS = 8
SPIMISO = 9
SPIMOSI = 10
SPICLK = 11
channel = 0

GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICS, GPIO.OUT)


i = 0
sum = 0
count = 0
keep_stop = 0
keep_move = 0
filename = "pirdata" + datetime.now().isoformat() + ".csv"
handle = open(filename,'a')
datalist = ["passingtime", "input"]
csv.writer(handle).writerow(datalist)
runtime = 20 #5400秒＝90分
start = time.time()
print ("start : " + str(start))

while (time.time() - start <= runtime):
	data = readadc(channel, SPICLK, SPIMOSI, SPIMISO, SPICS)
	passingtime = time.time() - start
	
	#sum = sum + data
	datalist = []
	datalist.append(passingtime)
	datalist.append(data)
	csv.writer(handle).writerow(datalist)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	    s.connect(('192.168.1.33', PORT))
	    data = str(datalist[1])
	    s.send(data.encode())
	    print(s.recv(BUFFER_SIZE).decode())
	i = i + 1
	time.sleep(1.0)
#print ((sum/10)+10000)
	print (i)
handle.close()
GPIO.cleanup()
