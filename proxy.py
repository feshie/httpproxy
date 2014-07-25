#!/usr/bin/python

import serial
from bottle import route, run, template, response, static_file

port = serial.Serial("/dev/ttyUSB0", baudrate=115200,timeout=60)

returnheadder=""
returndata=""

def fetchurl(URL):
	port.write(URL+"\n")		#send request to node
	print "Fetching URL: "+URL
	data = port.readline(10000)	#read the first respeonse line
	global returnheadder
	global returndata
	
	returnheadder=""		#clear any previous headders
	returndata=""			#clear any previous data
	fetchstate="sent"		#mark that request has been sent
	while data != "":
		#print repr(data)
		if fetchstate == "sent":		#ignore initial statements
			print repr(data)
			if data[0:5] == "HTTP/":	#now receiveing header
				fetchstate="headder"	#start saving headder
			if data == "Could not establish connection\n":
				return False

		if fetchstate == "headder":		#save headders for later processing
			#print "headder"
			if data=="\r\n":
				fetchstate="data"
				#print "now for the data"
			else:
				returnheadder+=data	#store headder details

		elif fetchstate=="data":
			#print "data :"
			if data=="Connection closed.\n": #if connection has been closed
				fetchstate="done"	#process any remaining debug messages
			else:
				returndata+=data	#store the data

		elif fetchstate=="done":
			#process final codes
			if data == "Status = 200\n":	#look for an end condition
				return 200		#return success

		data = port.readline(10000)	#read the next line for processing
	return False

def update_cache(url):
	try:
		f=open('cache/'+url,'w')
		f.write(returndata)
		f.close()
	except:
		print "unable to update cache for "+url

@route('/node/<url:path>')
def nodepages(url):
	if (fetchurl(url)):
		update_cache(url)
		return returndata
	else:
		response.status=504
		return "unable to comunicate with node page might be <a href=\"../cache/"+url+"\">cached</a>"

@route('/cache/<url:path>')
def send_cache(url):
	return static_file(url, root='cache/')

@route('/')
def index():
	#return "<html><body><p><a href=\"/node/2001:630:d0:f200:212:7400:1465:d8aa\">Border Router page</a></p></html>"
	return static_file("index.html", "")


if __name__ == "__main__":
#	print fetchurl("2001:630:d0:f200:212:7400:1465:d8aa")
#
#	print "headder"
#	print returnheadder
#	print "data"
#	print returndata

	run(host="localhost", port=8080)
