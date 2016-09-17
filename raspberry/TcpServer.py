
import socket 
import select
import sys
from hTools import Thread
import time

class TcpServer(Thread):
	def __init__(self, logger, handler, host, port=9877):

		self.logger = logger
		self.handler = handler
		self.connection = None

		self.tcpsocket = socket.socket()

		self.host = socket.gethostbyname(socket.getfqdn())
		self.host = host
		self.port = port
		self.logger.info('Starting TCP Server on ' + self.host + ':' + str(self.port) )


		self.Setup()

	def Setup(self):

		#Prevent socket.error: [Errno 98] Address already in use
		self.tcpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tcpsocket.bind((self.host, self.port))
		self.tcpsocket.setblocking(0)



	def Run(self):

	
		# Do not block forever (milliseconds)
		TIMEOUT = 1000

		## -- Listen and allow for a single connection
		self.logger.info('TCP Server is listening')
		self.tcpsocket.listen(1)
		
		##self.logger.info('TCP Connection started with ' + address[0] )

		READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR

		# Set up the poller
		poller = select.poll()
		poller.register(self.tcpsocket, READ_ONLY)

		# Map file descriptors to socket objects
		fd_to_socket = { self.tcpsocket.fileno(): self.tcpsocket,}

		while True:

			try:

				# Wait for at least one of the sockets to be ready for processing
				events = poller.poll(TIMEOUT)

				for fd, flag in events:

					# Retrieve the actual socket from its file descriptor
					s = fd_to_socket[fd]

					if flag & (select.POLLIN | select.POLLPRI):

						if s is self.tcpsocket:
							# A "readable" server socket is ready to accept a connection
							self.connection, address = s.accept()

							self.logger.info('TCP Connection started with ' + address[0] )
							self.connection.setblocking(0)
							fd_to_socket[ self.connection.fileno() ] = self.connection
							poller.register(self.connection, READ_ONLY)

						else:
							data = s.recv(1024)
							if data:
								self.handler(address[0], data)

					elif flag & select.POLLHUP:

						# Client hung up
						self.logger.info('Connection to ' + address[0] + " was terminated.")
						
						# Stop listening for input on the connection
						poller.unregister(s)
						s.close()

						## -- Listen and allow for a single connection
						self.logger.info('TCP Server is listening')
						self.tcpsocket.listen(1)

				time.sleep(2)

			except Exception as ex:
				self.logger.exception(ex)
				raise

		##while True:

			"""
			try:

				ready_to_read, ready_to_write, in_error = select.select([self.connection,], [self.connection,], [], 5)

			except select.error:
				self.logger.info('Connection error.')


				self.logger.info('Connection to ' + address[0] + " was terminated.")

				self.connection.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
				self.connection.close()

				self.logger.info('TCP Server is listening...')
				self.tcpsocket.listen(1)

				self.connection, address = self.tcpsocket.accept()
				self.logger.info('TCP Connection started with ' + address[0] )

			if len(ready_to_read) == 0:

			    data = self.connection.recv(1024)
			    if data:
			    	self.handler(address[0], data)

			print "ready to read: " + str(ready_to_read)
			print "ready to write: " + str(ready_to_write)
			print "ready to error: " + str(in_error)
			print
			"""

			##time.sleep(2)
			    




	def Run2(self):

		try:

			## -- Listen and allow for a single connection
			self.logger.info('TCP Server is listening')
			self.tcpsocket.listen(1)

			self.connection, address = self.tcpsocket.accept()
			self.logger.info('TCP Connection started with ' + address[0] )

			##self.handler(address[0], "init")

			while True:

			    data = self.connection.recv(1024)
			    if data:
			    	self.handler(address[0], data)

			    time.sleep(2)
			    


		except Exception as ex:
			self.logger.exception(ex)
			raise

	def Close(self):

		self.logger.info('Stopping TCP Server' )
		self.tcpsocket.close()