#Jacob Gavin
#Home.py
#Twisted Primer Assignment

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred

#Protocol for command connection
class HomeCommandConnection(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.commandConnection = self
		if(self.handler.clientConnection != ''):
			self.handler.requestDataConnection()
			
		return

#Protocol for data connection
class HomeDataConnection(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.dataConnection = self

		d = self.handler.queue.get()
		d.addCallback(self.handler.sendQueuedData)
		return

	def dataReceived(self, data):
		self.handler.forwardDataToClient(data)

#Protocol for client connection
class ClientConnectionProtocol(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.clientConnection = self
		DataFactory = DataConnectionFactory(self.handler)
		reactor.listenTCP(32003, DataFactory)

		self.handler.requestDataConnection()
		return

	def dataReceived(self, data):
		
		if(self.handler.dataConnection == ''):
			self.handler.queue.put(data)
		else:
			self.handler.forwardClientToData(data)


#Factory for command connection
class CommandConnectionFactory(Factory):

	def __init__(self, handler):
		self.handler = handler

    	def buildProtocol(self, addr):
       		return HomeCommandConnection(self.handler)

#Factory for client connection
class ClientConnectionFactory(Factory):

	def __init__(self, handler):
		self.handler = handler	

    	def buildProtocol(self, addr):
       		return ClientConnectionProtocol(self.handler)

#Factory for data connection
class DataConnectionFactory(Factory):

	def __init__(self, handler):
		self.handler = handler

    	def buildProtocol(self, addr):
       		return HomeDataConnection(self.handler)
	
#Handler which holds copies of every connection and handles all interaction between connections
class HomeConnectionHandler:


	#Initialize to connections to empty string and create deferred queue
	def __init__(self):

		self.commandConnection = ''
		self.dataConnection = ''
		self.clientConnection = ''
		self.queue = DeferredQueue()

	#Send request to work on command connection
	def requestDataConnection(self):
		self.commandConnection.sendLine("1")

	#Bridge data to client
	def forwardDataToClient(self, data):
		self.clientConnection.transport.write(data)

	#Bridge client to data
	def forwardClientToData(self, data):
		self.dataConnection.transport.write(data)

	#Send data stored up in queue until queue is empty
	def sendQueuedData(self, data):
		if(data):
			self.dataConnection.transport.write(data)
		self.queue.get().addCallback( self.sendQueuedData )

#Create connectionHandler and pass it to factories
connectionHandler = HomeConnectionHandler()
CommandFactory = CommandConnectionFactory(connectionHandler)
ClientFactory = ClientConnectionFactory(connectionHandler)

#Listen For Connections from Work and direct to Command and Client Factories
reactor.listenTCP(32004, CommandFactory)
reactor.listenTCP(9003, ClientFactory)

#Start event loop
reactor.run()

