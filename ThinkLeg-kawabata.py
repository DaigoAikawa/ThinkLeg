# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import csv
from statistics import stdev
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

runtime = 4800 #run time
start = time.time()
interval = 0.1
nexttime = interval

dataque = []
filename = "ThinkLegdata" + datetime.now().isoformat() + ".csv"
handle = open(filename,'a')
datalist = ["passingtime", "input", "standard_deviation", "is_moving"]

def checkque (data):
	is_moving = 0
	standard_deviation = 0.0
	global dataque
	dataque.append(data)

	if (len(dataque) == 10) :
		standard_deviation = stdev(dataque)
	elif (len(dataque) > 10) :
		dataque.pop(0)
		standard_deviation = stdev(dataque)

	if (standard_deviation >= 17) :
		is_moving = 1

	return (standard_deviation, is_moving)

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
			std_flag = checkque(data)
			standard_deviation = std_flag[0]
			datalist.append(standard_deviation)
			is_moving = std_flag[1]
			datalist.append(is_moving)
			print(str(passingtime)+" "+str(data)+" "+str(standard_deviation)+" "+str(is_moving))
	
			csv.writer(handle).writerow(datalist)
			#print(datalist)
			nexttime = nexttime + interval
		else:
			continue
except KeyboardInterrupt as e:
	print(e)
finally:
	handle.close()
	GPIO.cleanup()

