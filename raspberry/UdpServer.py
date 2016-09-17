import socket

class UdpServer():
	def __init__(self, logger, broadcast_address, broadcast_port):

		## -- Configure for broadcast
		self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		self.host = socket.gethostbyname(socket.getfqdn())

		logger.info('Starting UDP Broadcast on ' + self.host + ':' + str(broadcast_port) + ' to ' + broadcast_address + ":" + str(broadcast_port) )

	def GetSocket(self):

		return self.broadcast_socket