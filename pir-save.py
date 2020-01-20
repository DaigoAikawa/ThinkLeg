# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

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

runtime = 5400 #5400秒＝90分
start = time.time()
i = 0
sum = 0
count = 0
keep_stop = 0
keep_move = 0
filename = "pirdata" + datetime.now().isoformat() + ".csv"
handle = open(filename,'a')
datalist = ["passingtime", "input", "count"]
csv.writer(handle).writerow(datalist)
print ("start : " + str(start))
while (time.time() - start <= runtime or i <= 10800):
	data = readadc(channel, SPICLK, SPIMOSI, SPIMISO, SPICS)
	passingtime = time.time() - start
	if (data > 820 or data < 730) :
		if (keep_move == 1) :
			count = count + 1
		keep_move = keep_move + 1
		keep_stop = 0
	else:
		keep_stop = keep_stop + 1
	if (keep_stop >= 2) :
		keep_move = 0
	if (keep_move >= 8) :
		keep_move = 0
	if (i % 2 == 0) :
		print ("passing time" + str(passingtime))
		print ("input : " + str(data))
		print ("count : " + str(count))
	#sum = sum + data
	datalist = []
	datalist.append(passingtime)
	datalist.append(data)
	datalist.append(count)
	csv.writer(handle).writerow(datalist)
	i = i + 1
	time.sleep(0.5)
#print ((sum/10)+10000)
print (i)
handle.close()
GPIO.cleanup()
