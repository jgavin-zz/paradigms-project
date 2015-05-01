#Jacob Gavin & James Harkins
#game_server.py
#Twisted Primer Assignment

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred

#Protocol for temp connection
class TempProtocol(LineReceiver):

	def __init__(self, handler):
			self.handler = handler
			
			    	def connectionMade(self):
			    			if(self.handler.connectionMade == 0):
			    						self.handler.connectionMade = 1
			    									self.sendLine("1")
			    											else:
			    														self.sendLine("2")
			    																return
			    																
			    																#Protocol for player1 connection
			    																class Player1Protocol(LineReceiver):
			    																
			    																	def __init__(self, handler):
			    																			self.handler = handler
			    																			
			    																			    	def connectionMade(self):
			    																			    			self.handler.player1Connection = self
			    																			    			
			    																			    				def dataReceived(self, data):
			    																			    						print data
			    																			    						
			    																			    						#Protocol for player2 connection
			    																			    						class Player2Protocol(LineReceiver):
			    																			    						
			    																			    							def __init__(self, handler):
			    																			    									self.handler = handler
			    																			    									
			    																			    									    	def connectionMade(self):
			    																			    									    			self.handler.player2Connection = self
			    																			    									    					self.handler.tellPlayersToStart()
			    																			    									    							return
			    																			    									    							
			    																			    									    								def dataReceived(self, data):
			    																			    									    										print data
			    																			    									    										
			    																			    									    										#Factory for client1 connection
			    																			    									    										class TempFactory(Factory):
			    																			    									    										
			    																			    									    											def __init__(self, handler):
			    																			    									    													self.handler = handler	
			    																			    									    													
			    																			    									    													    	def buildProtocol(self, addr):
			    																			    									    													    	       		return TempProtocol(self.handler)
			    																			    									    													    	       		
			    																			    									    													    	       		#Factory for client1 connection
			    																			    									    													    	       		class Player1Factory(Factory):
			    																			    									    													    	       		
			    																			    									    													    	       			def __init__(self, handler):
			    																			    									    													    	       					self.handler = handler	
			    																			    									    													    	       					
			    																			    									    													    	       					    	def buildProtocol(self, addr):
			    																			    									    													    	       					    	       		return Player1Protocol(self.handler)
			    																			    									    													    	       					    	       		
			    																			    									    													    	       					    	       		#Factory for client2 connection
			    																			    									    													    	       					    	       		class Player2Factory(Factory):
			    																			    									    													    	       					    	       		
			    																			    									    													    	       					    	       			def __init__(self, handler):
			    																			    									    													    	       					    	       					self.handler = handler	
			    																			    									    													    	       					    	       					
			    																			    									    													    	       					    	       					    	def buildProtocol(self, addr):
			    																			    									    													    	       					    	       					    	       		return Player2Protocol(self.handler)
			    																			    									    													    	       					    	       					    	       		
			    																			    									    													    	       					    	       					    	       			
			    																			    									    													    	       					    	       					    	       			#Handler which holds copies of every connection and handles all interaction between connections
			    																			    									    													    	       					    	       					    	       			class GameHandler:
			    																			    									    													    	       					    	       					    	       			
			    																			    									    													    	       					    	       					    	       			
			    																			    									    													    	       					    	       					    	       				#Initialize to connections to empty string and create deferred queue
			    																			    									    													    	       					    	       					    	       					def __init__(self):
			    																			    									    													    	       					    	       					    	       					
			    																			    									    													    	       					    	       					    	       							self.connectionMade = 0
			    																			    									    													    	       					    	       					    	       									self.player1Connection = ''
			    																			    									    													    	       					    	       					    	       											self.player2Connection = ''
			    																			    									    													    	       					    	       					    	       											
			    																			    									    													    	       					    	       					    	       												def tellPlayersToStart(self):
			    																			    									    													    	       					    	       					    	       														self.player1Connection.transport.write('start')
			    																			    									    													    	       					    	       					    	       																self.player2Connection.transport.write('start')
			    																			    									    													    	       					    	       					    	       																
			    																			    									    													    	       					    	       					    	       																#Create connectionHandler and pass it to factories
			    																			    									    													    	       					    	       					    	       																gameHandler = GameHandler()
			    																			    									    													    	       					    	       					    	       																tempFactory = TempFactory(gameHandler)
			    																			    									    													    	       					    	       					    	       																player1Factory = Player1Factory(gameHandler)
			    																			    									    													    	       					    	       					    	       																player2Factory = Player2Factory(gameHandler)
			    																			    									    													    	       					    	       					    	       																
			    																			    									    													    	       					    	       					    	       																#Listen For Connections from Work and direct to Command and Client Factories
			    																			    									    													    	       					    	       					    	       																reactor.listenTCP(32000, tempFactory)
			    																			    									    													    	       					    	       					    	       																reactor.listenTCP(32001, player1Factory)
			    																			    									    													    	       					    	       					    	       																reactor.listenTCP(32002, player2Factory)
			    																			    									    													    	       					    	       					    	       																
			    																			    									    													    	       					    	       					    	       																#Start event loop
			    																			    									    													    	       					    	       					    	       																reactor.run()
			    																			    									    													    	       					    	       					    	       																
