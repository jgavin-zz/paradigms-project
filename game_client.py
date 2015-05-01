#Jacob Gavin & James Harkins
#game_client.py
#Twisted Primer Assignment

from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred
import GameSpace from game


#Protocol for command connection
class PlayerConnectionProtocol(Protocol):

	def __init__(self, handler):
			self.handler = handler
			
				def connectionMade(self):
						self.handler.connection  = self
						
							def dataReceived(self, data):
									if(data == 'start'):
												self.handler.startGame()
												
												#Protocol for command connection
												class InitialConnectionProtocol(Protocol):
												
													def __init__(self, handler):
															self.handler = handler
															
																def connectionMade(self):
																		self.handler.tempconnection  = self
																		
																			def dataReceived(self, data):
																					data = int(data[0])
																							if(data == 1):
																										reactor.connectTCP('student00.cse.nd.edu', 32001, PlayerConnectionFactory(self.handler))
																												if(data == 2):
																															reactor.connectTCP('student00.cse.nd.edu', 32002, PlayerConnectionFactory(self.handler))
																																	
																																	
																																	#Factory for initial connection factory
																																	class InitialConnectionFactory(ClientFactory):
																																	
																																		def __init__(self, handler):
																																				self.handler = handler
																																				
																																					def buildProtocol(self, addr):
																																							
																																									return InitialConnectionProtocol(self.handler)
																																									
																																									#Factory for initial connection factory
																																									class PlayerConnectionFactory(ClientFactory):
																																									
																																										def __init__(self, handler):
																																												self.handler = handler
																																												
																																													def buildProtocol(self, addr):
																																															
																																																	return PlayerConnectionProtocol(self.handler)
																																																	
																																																	#Handler which stores copies of all connections and handles all interactions between connections
																																																	class GameHandler:
																																																	
																																																		#Initialize connections to empty string and construct deferred queue
																																																			def __init__(self):
																																																			
																																																					self.connection = ''
																																																							self.tempconnection = ''
																																																							
																																																								def startGame(self):
																																																										print "Game Started"
																																																												gs = GameSpace(self.connection)
																																																														gs.main()
																																																														
																																																														#Instantiate handler and pass to command factory
																																																														gameHandler = GameHandler()										
																																																														initialConnectionFactory = InitialConnectionFactory(gameHandler)	
																																																														
																																																														#Create command connection to home									
																																																														reactor.connectTCP('student00.cse.nd.edu', 32000, initialConnectionFactory)
																																																															
																																																															#Start event loop									
																																																															reactor.run()
