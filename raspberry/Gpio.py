from hTools import Thread
import RPi.GPIO as GPIO
import ConfigParser
from datetime import datetime
import time
import random
import socket
import json
from TcpServer import TcpServer
from UdpServer import UdpServer


class Gpio(Thread):
	def __init__(self, logger, broadcast_address, broadcast_port, tcp_address, tcp_port):
		
		self.logger = logger
		self.broadcast_address = broadcast_address
		self.broadcast_port = broadcast_port

		## Setup public read-only UDP broadcast server
		self.udpServer = UdpServer(logger, broadcast_address, broadcast_port)
		self.broadcast_socket = self.udpServer.GetSocket()

		## -- Init TCP Server and wait for connection
		self.tcpServer = TcpServer(logger, self.TcpHandler, tcp_address, tcp_port)
		self.tcpServer.Start()

		## -- Initialise Raspbery GPIO
		GPIO.setmode(GPIO.BOARD)
		GPIO.cleanup()
		self.logger.info('Mode is Boardpins')

		self.gpios = {}
		self.inputs = []
		self.outputs = []

		self.enableSimulator = False

		## -- Configure GPIO pins
		self.Setup()



	def TcpHandler(self, address, message):

		# -- TCP Message callback handler
		self.logger.info('Received Message from ' + address + ' - ' + message)
		package = None
		
		if message == "init":

			## -- Write the full gpio register back to client
			package = {"cmd":"init", "data": self.gpios}

		if message == "inputs":

			## -- Write the inputs gpio register back to client
			package = {"cmd":"inputs", "data": self.inputs}

		if message == "outputs":

			## -- Write the full outputs register back to client
			package = {"cmd":"outputs", "data": self.outputs}


		elif message[0:3] == "wo:":
			
			## -- Unwrap Message
			m = message.split(":")
			pin = int(m[1])
			value = int(m[2])

			## -- Find the GPIO
			gpio = self.gpios[ pin ]

			## -- Set GPIO
			GPIO.output( pin, value )
			self.logger.info("Remote device " + address + ' set ' + gpio["tag"] + " to " + str(value) )

			## -- Set state change in dictionary
			gpio["value"] = value
			gpio["datetime"] = str(datetime.now())
			self.gpios[ pin ] = gpio

			## -- Respond when done
			package = { "cmd": "gpio", "data": gpio }

		if package:
			self.tcpServer.connection.send( json.dumps(package) )
			self.logger.info('Sent TCP Message to ' + address + ' - ' + str(package) )




	def Setup(self):

		## -- Get Pins from conf
		config_filename = 'pinmap_modelb.conf'
		self.logger.info('Load Pin Map (' + config_filename + ')')
		config = ConfigParser.ConfigParser()
		file_handle = open(config_filename)
		config.readfp(file_handle)

		for section in config.sections():

			gpio = {}

			## -- Set Pin Dictionary
			gpio["tag"] = section
			gpio["name"] = config.get(section, "name")
			gpio["pin"] = config.getint(section, "pin")
			gpio["value"] = config.getint(section, "value")
			gpio["input"] = config.getint(section, "input")
			gpio["datetime"] = str(datetime.now())

			if gpio["input"]:

				self.logger.info(' ... Set ' + section + ' as Input on pin ' + str(gpio["pin"]) )

				if gpio["value"] == 1:
					pull_up_down = GPIO.PUD_UP
				else:
					pull_up_down = GPIO.PUD_DOWN

				## -- Set as pin Input and force state
				GPIO.setup(gpio["pin"], GPIO.IN, pull_up_down=pull_up_down)

				## -- Add trigger for pin state change
				GPIO.add_event_detect(gpio["pin"], GPIO.BOTH, callback=self.CallbackInput)

				## -- Add to class Inputs dictionary
				self.inputs.append(gpio)

			else:

				self.logger.info(' ... Set ' + section + ' as Output on pin ' + str(gpio["pin"]) )

				## -- Set as pin Output and force state 
				GPIO.setup(gpio["pin"], GPIO.OUT, initial=gpio["pin"])	

				## -- Add to class Outputs dictionary
				self.outputs.append(gpio)						


			## -- Maintain a dictionary of pin dictionaries
			self.gpios[ gpio["pin"] ] = gpio


	def CallbackInput(self, channel):

		## -- Find GPIO channel in gpios dictionary
		gpio = self.gpios[ channel ]

		## -- Set state change in dictionary
		gpio["value"] = GPIO.input(channel)
		gpio["datetime"] = str(datetime.now())

		msg = ' ... Broadcast: ' + gpio["tag"] + ' changed to ' + str(GPIO.input(channel))
		self.logger.info( msg )

		## -- Broadcast gpio state change on Udp
		package = { "cmd":"gpio", "data":gpio }
		self.broadcast_socket.sendto(json.dumps(package), (self.broadcast_address, self.broadcast_port))



	def Run(self):

		try:

			if self.enableSimulator:
				self.logger.info('Start Simulator...')

			while True:

				## -- Start Simulator
				if self.enableSimulator:
					
					self.Simulator()
			

		except Exception as ex:
			self.logger.exception(ex)
			raise

	def Simulator(self):

		## -- Load random sleep and random gpio input
		wait = random.randrange(1,10)
		idx = random.randrange(0, len(self.inputs) - 1)

		gpio = self.inputs[idx]

		## -- Pull Up if down and Pull Down if up
		if GPIO.input(gpio["pin"]):
			GPIO.setup(gpio["pin"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		else:
			GPIO.setup(gpio["pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

		self.logger.info(' ... GPIO ' + gpio['tag'] + ' set to ' + str(GPIO.input(gpio["pin"])) )

		time.sleep(wait)

	def Close(self):

		self.logger.info('Close GPIO thread' )
		if self.tcpServer:
			self.tcpServer.Close()
			self.tcpServer.Stop()



