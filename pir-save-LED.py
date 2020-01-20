# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

import RPi.GPIO as GPIO
import time


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
GPIO.setup(25, GPIO.OUT)
GPIO.output(25, GPIO.HIGH)

runtime = 300 #run time
high = 820
low = 730
start = time.time()
interval = 0.1
nexttime = interval

datastock = []
filename = "pirdata" + datetime.now().isoformat() + ".csv"
handle = open(filename,'a')
datalist = ["passingtime", "input", "flag"]

def checkstock (datadata):
	flag = 0
	count = 0
	for item in datadata:
		if (item >= 820 or item <= 720):
			count += 1
	if (count != 0):
			flag = 1
	return flag

csv.writer(handle).writerow(datalist)
print ("start : " + str(start))
try:
	while (time.time() - start <= + runtime):
		passingtime = time.time() - start
		datalist = []
		datalist.append(passingtime)
		#print(passingtime)
		if (passingtime >= nexttime):
			data = readadc(channel, SPICLK, SPIMOSI, SPIMISO, SPICS)
			datalist.append(data)
			print(str(passingtime)+" "+str(data))

			if(len(datastock) >= 2):
				for j in range(1):
					datastock[j] = datastock[j+1]
				datastock[1] = data
			else:
				datastock.append(data)
			print(datastock)
	
			if(checkstock(datastock)):
				datalist.append(1)
			else:
				datalist.append(0)
	
			csv.writer(handle).writerow(datalist)
			print(datalist)
			nexttime = nexttime + interval
		else:
			continue
except KeyboardInterrupt as e:
	print(e)
finally:
	handle.close()
	GPIO.cleanup()

