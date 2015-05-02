#Jacob Gavin & James Harkins
#game_server.py
#Twisted Primer Assignment

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred
import json
import cPickle as pickle
from math import *
import sys
import os
import random

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
		data = json.loads(data)
		self.handler.processPlayer1Events(data)	
		return

#Protocol for player2 connection
class Player2Protocol(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.player2Connection = self
		self.handler.tellPlayersToStart()
		return

	def dataReceived(self, data):
		data = json.loads(data)
		self.handler.processPlayer2Events(data)		
		return
		

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


class EnemyData:

	def __init__(self, enemyID):

		self.enemyID = enemyID
		self.target = 0
		self.xcenter = 450
		self.ycenter = 200
		self.angle = 90
		self.alive = 1

	def setTarget(self, x1, y1, x2, y2):

		dx1 = self.xcenter - x1
		dy1 = self.ycenter - y1

		dx2 = self.xcenter - x2
		dy2 = self.ycenter - y2
	
		if( hypot(dx1, dy1) <= hypot(dx2, dy2) ):
			self.target = 1
		else:
			self.target = 2
		

	def move(self, playerxcenter, playerycenter):

		#First set angle
		dx = self.xcenter - playerxcenter
		dy = self.ycenter - playerycenter
		rangle = atan2(dy, -dx)
		self.angle  = degrees(rangle) - 90
		
		#Move x and y
		if( hypot(dx, dy) > 100 ):
			angle = self.angle + 90
			angle = radians(angle)

			self.xcenter = self.xcenter + int( cos(angle) * 20 )
			self.ycenter = self.ycenter - int( sin(angle) * 20 )
		

class BulletData:

	def __init__(self, bulletID, playerID, playerxcenter, playerycenter, angle, gunLength):

		self.bulletID = bulletID
		self.playerID = playerID
		self.xcenter = 0
		self.ycenter = 0
		self.vx = 0
		self.vy = 0
		self.angle = degrees(angle) + 90
		self.alive = 1

		self.setInitialPosition(playerxcenter, playerycenter, angle, gunLength)
		self.setInitialVelocity(angle)

	def setInitialPosition(self, playerxcenter, playerycenter, angle, gunLength):
	
		angle = self.angle + 90

		angle = radians(angle)

		self.xcenter = playerxcenter + int( cos(angle) * gunLength/2 )
		self.ycenter = playerycenter - int( sin(angle) * gunLength/2 )		

	def setInitialVelocity(self, angle):

		self.vx = cos(angle) * 10
		self.vy = sin(angle) * 10

	def move(self):

		self.xcenter = int(self.xcenter - self.vx)
		self.ycenter = int(self.ycenter + self.vy)

	
#Handler which holds copies of every connection and handles all interaction between connections
class GameHandler:


	#Initialize to connections to empty string and create deferred queue
	def __init__(self):

		self.connectionMade = 0
		self.player1Connection = ''
		self.player2Connection = ''

		self.player1x = 100
		self.player1y = 100
		self.player2x = 200
		self.player2y = 200

		self.player1GunAngle = 270
		self.player2GunAngle = 270

		self.player1Angle = 90
		self.player2Angle = 90

		self.r1Angle = 0
		self.r2Angle = 0

		self.gunLength = 80

		self.enemies = []
		self.bullets = []

		self.gamecounter = 0
		

	def tellPlayersToStart(self):
		self.sendGameData(1)
		self.sendGameData(2)

	def processPlayer1Events(self, events):
		self.gamecounter = self.gamecounter + 1
		
		if(self.gamecounter%25 == 0):
			self.enemies.append(EnemyData(len(self.enemies) + 1))
			self.enemies[len(self.enemies) - 1].setTarget(self.player1x, self.player1y, self.player2x, self.player2y)

		mx = events['mx']
		my = events['my']
		#if events['exit']:
		#	self.exitGame()

		direction = events["keyPressed"]
		if( direction != '' ):
			self.movePlayer(1, direction)

		self.computeAngle(1, mx, my)

		#Move bullets
		for b in self.bullets:
			if(b.playerID == 1 and b.alive == 1):
				b.move()

		if( events["mouseEvent"] == 'Pressed' ):
			self.bullets.append( BulletData(len(self.bullets) + 1, 1, self.player1x, self.player1y, self.r1Angle, self.gunLength))

		for e in self.enemies:
			if(e.target == 1 and e.alive == 1):
				e.move(self.player1x, self.player1y)

		self.sendGameData(1)
		return

	def processPlayer2Events(self, events):
		mx = events['mx']
		my = events['my']

		direction = events["keyPressed"]
		if( direction != '' ):
			self.movePlayer(2, direction)

		self.computeAngle(2, mx, my)

		#Move bullets
		for b in self.bullets:
			if(b.playerID == 2 and b.alive == 1):
				b.move()

		if( events["mouseEvent"] == 'Pressed' ):
			self.bullets.append( BulletData(len(self.bullets) + 1, 2, self.player2x, self.player2y, self.r2Angle, self.gunLength))

		for e in self.enemies:
			if(e.target == 2 and e.alive == 1):
				e.move(self.player2x, self.player2y)

		self.sendGameData(2)
		return

	def movePlayer(self, playerID, direction):
		if(direction == 'Right'):
			if playerID == 1:
				self.player1x = self.player1x + 10
				self.player1Angle = 90
			if playerID == 2:
				self.player2x = self.player2x + 10
				self.player2Angle = 90

		if(direction == 'Left'):
			if playerID == 1:
				self.player1x = self.player1x - 10
				self.player1Angle = 270
			if playerID == 2:
				self.player2x = self.player2x - 10
				self.player2Angle = 270

		if(direction == 'Up'):
			if playerID == 1:
				self.player1y = self.player1y - 10
				self.player1Angle = 180
			if playerID == 2:
				self.player2y = self.player2y - 10
				self.player2Angle = 180

		if(direction == 'Down'):
			if playerID == 1:
				self.player1y = self.player1y + 10
				self.player1Angle = 0
			if playerID == 2:
				self.player2y = self.player2y + 10
				self.player2Angle = 0

		return

	def computeAngle(self, playerID, mx, my):

		if(playerID == 1):
			dx = mx - (self.player1x)
			dy = my - (self.player1y)
			self.r1Angle = atan2(dy, -dx)
			self.player1GunAngle  = degrees(self.r1Angle) + 90

		if(playerID == 2):
			dx = mx - (self.player2x)
			dy = my - (self.player2y)
			self.r2Angle = atan2(dy, -dx)
			self.player2GunAngle  = degrees(self.r2Angle) + 90

	def exitGame(self):
		data = {}
		data['exit'] = 1
		data = json.dumps(data)
		self.player1Connection.transport.write(data)
		self.player2Connection.transport.write(data)

	def sendGameData(self, playerID):

		data = {}
		data['player1x'] = self.player1x
		data['player1y'] = self.player1y
		data['player2x'] = self.player2x
		data['player2y'] = self.player2y
		data['exit'] = 0

		if(playerID == 1):
			data['partnerGunAngle'] = self.player2GunAngle
		if(playerID == 2):
			data['partnerGunAngle'] = self.player1GunAngle

		data['player1Angle'] = self.player1Angle
		data['player2Angle'] = self.player2Angle

		data['bullets'] = []
		for b in self.bullets:
			data['bullets'].append({'bulletID' : b.bulletID, 'x':b.xcenter, 'y':b.ycenter, 'angle':b.angle})

		data['enemies'] = []
		for e in self.enemies:
			data['enemies'].append({'enemyID' : e.enemyID, 'x':e.xcenter, 'y':e.ycenter, 'angle':e.angle})
		

		data = json.dumps(data)
		
		if(playerID == 1):
			self.player1Connection.transport.write(data)
		if(playerID == 2):
			self.player2Connection.transport.write(data)
	

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

