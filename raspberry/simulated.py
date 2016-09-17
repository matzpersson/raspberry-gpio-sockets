##
##  broadcast.py
##  Udp Broadcase Example
##
##  Created by Matz Persson on 23/02/2015.
##  Copyright 2016 Headstation. All rights reserved.  It is free software and may be redistributed under the terms specified in the LICENSE file (Apache License 2.0). 
##

import os
import sys
import time
import socket
import random
import hTools
from Gpio import Gpio

## -- Configure addresses
broadcast_address = '172.16.1.255'
broadcast_port = 54545
tcp_address = '172.16.1.51'
tcp_port = 9877

## -- Setup and start global logger
level_name = 'info' 
logfile_prefix = None
logger = hTools.initLogging(logfile_prefix, level_name, 'raspberry_gpio_simulator')

logger.info('## ------------------------------------------------------------- ##') 
logger.info('## STARTING Headstation Raspberry GPIO Simulator daemon -------- ##') 
logger.info('## ------------------------------------------------------------- ##') 

## -- Start gpio sockets up as thread
logger.info('Starting services...') 
gpio = Gpio(logger, broadcast_address, broadcast_port, tcp_address, tcp_port)
gpio.enableSimulator = True
gpio.Start()

while True:

	## -- Wait for Q for Quit
	i = raw_input()
	if i == 'q':

		gpio.Close()
		gpio.Stop()
		logger.info('User Quit, Thread killed...., Bye' )

		break

