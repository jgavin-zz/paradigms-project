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
import time

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

	def dataReceived(self, data):
		if data == "Clicked":
			self.handler.playersStarted += 1
			self.sendLine("3")
		if self.handler.playersStarted == 2:
			self.handler.started = 1

#Protocol for player1 connection
class Player1Protocol(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.player1Connection = self
		if self.handler.started:
			self.handler.tellPlayersToStart()
			self.handler.started = 0

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
		if self.handler.started:
			self.handler.tellPlayersToStart()
			self.handler.started = 0
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

			self.xcenter = self.xcenter + int( (cos(angle) * 20)/15 )
			self.ycenter = self.ycenter - int( (sin(angle) * 20)/15 )

	def getPos(self):
		return self.xcenter, self.ycenter	
		

class BulletData:

	def __init__(self, bulletID, playerID, playerxcenter, playerycenter, angle, gunLength, btype = 0):

		self.bulletID = bulletID
		self.playerID = playerID
		self.xcenter = 0.0
		self.ycenter = 0.0
		self.vx = 0.0
		self.vy = 0.0
		self.angle = degrees(angle) + 90
		self.alive = 1

		self.setInitialPosition(playerxcenter, playerycenter, angle, gunLength)
		self.setInitialVelocity(angle)
		self.type = btype

	def setInitialPosition(self, playerxcenter, playerycenter, angle, gunLength):
	
		angle = self.angle + 90

		angle = radians(angle)

		self.xcenter = playerxcenter + cos(angle) * gunLength/2
		self.ycenter = playerycenter - sin(angle) * gunLength/2		

	def setInitialVelocity(self, angle):

		self.vx = (cos(angle) * 10)/6
		self.vy = (sin(angle) * 10)/6

	def move(self):

		self.xcenter = self.xcenter - self.vx
		self.ycenter = self.ycenter + self.vy

	def getPos(self):
		return self.xcenter,self.ycenter

	
#Handler which holds copies of every connection and handles all interaction between connections
class GameHandler:


	#Initialize to connections to empty string and create deferred queue
	def __init__(self):

		self.connectionMade = 0
		self.playersStarted = 0
		self.player1Connection = ''
		self.player2Connection = ''

		self.player1x = 100
		self.player1y = 100
		self.player2x = 200
		self.player2y = 200
		
		self.player1health = 10
		self.player2health = 10

		self.player1alive = 1
		self.player2alive = 1

		self.player1GunAngle = 270
		self.player2GunAngle = 270

		self.player1Angle = 90
		self.player2Angle = 90

		self.player1Kills = 0
		self.player2Kills = 0

		self.delay = 5

		self.player1DeadTime = 0
		self.player2DeadTime = 0

		self.r1Angle = 0
		self.r2Angle = 0

		self.gunLength = 80

		self.timer = 60	
					
		self.enemies = []
		self.bullets = []

		self.gamecounter = 0
		
		self.check = 0
		self.IDcount = 0
		self.eCount = 0

		self.started = 0

		self.number = 500

	def tellPlayersToStart(self):
		self.startTime = time.time()
		self.sendGameData(1)
		self.sendGameData(2)

	def processPlayer1Events(self, events):
		self.gamecounter = self.gamecounter + 1
		if(self.gamecounter%int(self.number) == 0 or self.gamecounter == 10):
			self.enemies.append(EnemyData(self.eCount))
			random.seed()
			number = random.randrange(0,4,1)
			if number == 0:
				self.enemies[len(self.enemies) - 1].xcenter = 60
				self.enemies[len(self.enemies) - 1].ycenter = 60 
			elif number == 1:
				self.enemies[len(self.enemies) - 1].xcenter = 60
				self.enemies[len(self.enemies) - 1].ycenter = 440
			elif number == 2:
				self.enemies[len(self.enemies) - 1].xcenter = 590
				self.enemies[len(self.enemies) - 1].ycenter = 60  
			else:
				self.enemies[len(self.enemies) - 1].xcenter = 590
				self.enemies[len(self.enemies) - 1].ycenter = 440
			self.enemies[len(self.enemies) - 1].setTarget(self.player1x, self.player1y, self.player2x, self.player2y)
			self.eCount+=1

		if not self.player1alive and time.time() - self.player1DeadTime > self.delay:
			self.player1alive = 1
			self.player1health = 10

		if events['exit'] == "1":
			self.player1Connection.transport.loseConnection()
			self.player2Connection.transport.loseConnection()
			reactor.stop()
			return

		mx = events['mx']
		my = events['my']
		#if events['exit']:
		#	self.exitGame()

		direction = events["keyPressed"]
		if( direction != '' and self.player1alive):
			self.movePlayer(1, direction)

		self.computeAngle(1, mx, my)

		#Move bullets
		for b in self.bullets:
			if(b.playerID == 1 and b.alive == 1):
				b.move()
				bulletX, bulletY = b.getPos()
				if self.player2alive:
					if bulletX >= self.player2x - 30 and bulletX <= self.player2x + 30:
						if bulletY >= self.player2y - 20 and bulletY <= self.player2y + 20:
							if b in self.bullets:
									self.bullets.remove(b)
							if b.type == 3:
								self.player2health -=1
								if self.player2health == 0:
									self.player2alive = 0
									self.player2DeadTime = time.time()
							continue
						
					if bulletX <= 0 or bulletY <= 0 or bulletX >= 650 or bulletY >= 500:
						if b in self.bullets:
							self.bullets.remove(b)
						continue

				for e in self.enemies:
						if bulletX >= e.xcenter - 20 and bulletX <= e.xcenter + 20:
							if bulletY >= e.ycenter - 10 and bulletY <= e.ycenter + 10:
								if b in self.bullets:
									self.bullets.remove(b)
								if e in self.enemies:
									self.enemies.remove(e)	
								if self.number > 20:
									self.number *= .95
								if b.type != 3:
									self.player1Kills += 1
								continue	
			if (b.type == 3):
				 bulletX, bulletY = b.getPos()
				 if self.player2alive:
				 	if bulletX >= self.player2x - 30 and bulletX <= self.player2x + 30:
						if bulletY >= self.player2y - 20 and bulletY <= self.player2y + 20:
							if b in self.bullets:
								self.bullets.remove(b)
							self.player2health -=1
							if self.player2health == 0:
								self.player2alive = 0
								self.player2DeadTime = time.time()
							continue
					if bulletX <= 0 or bulletY <= 0 or bulletX >= 650 or bulletY >= 500:
						if b in self.bullets:
							self.bullets.remove(b)

		if( events["mouseEvent"] == 'Pressed' and self.player1alive):
			self.bullets.append( BulletData(self.IDcount, 1, self.player1x, self.player1y, self.r1Angle, self.gunLength))
			self.IDcount+=1

		for e in self.enemies:
			if self.player1alive and self.player2alive:
				e.setTarget(self.player1x, self.player1y, self.player2x, self.player2y)
			elif self.player1alive:
				e.target = 1
			elif self.player2alive:
				e.target = 2
			if(e.target == 1 and e.alive == 1):
				e.move(self.player1x, self.player1y)
				if(random.randrange(0,100,1) == 1):
					if self.player1alive:
						self.enemyFire(e.getPos(),1,3)
			

		self.sendGameData(1)
		return

	def processPlayer2Events(self, events):
		if events['exit'] == "1":
			self.player1Connection.transport.loseConnection()
			self.player2Connection.transport.loseConnection()
			reactor.stop()
			return

		if not self.player2alive and time.time() - self.player2DeadTime > self.delay:
			self.player2alive = 1
			self.player2health = 10

		mx = events['mx']
		my = events['my']

		direction = events["keyPressed"]
		if( direction != '' and self.player2alive):
			self.movePlayer(2, direction)

		self.computeAngle(2, mx, my)

		
		for b in self.bullets:
			if(b.playerID == 2 and b.alive == 1):
				b.move()
				bulletX, bulletY = b.getPos()
				if self.player1alive:
					if bulletX >= self.player1x - 30 and bulletX <= self.player1x + 30:
						if bulletY >= self.player1y - 20 and bulletY <= self.player1y + 20:
							if b in self.bullets:
									self.bullets.remove(b)
							if b.type == 3:
								self.player1health -=1
								if self.player1health == 0:
									self.player1alive = 0
									self.player1DeadTime = time.time()
							continue
						
					if bulletX <= 0 or bulletY <= 0 or bulletX >= 650 or bulletY >= 500:
						if b in self.bullets:
							self.bullets.remove(b)
						continue
				
				for e in self.enemies:
						if bulletX >= e.xcenter - 20 and bulletX < e.xcenter + 20:
							if bulletY >= e.ycenter - 10 and bulletY <= e.ycenter + 10:
								if b in self.bullets:
									self.bullets.remove(b)
								if e in self.enemies:
									self.enemies.remove(e)
								if self.number > 20:
									self.number *= .95
								if b.type != 3:
									self.player2Kills += 1
								continue				
	
			elif (b.type == 3):
				bulletX, bulletY = b.getPos()
				if self.player1alive:
					if bulletX >= self.player1x - 30 and bulletX <= self.player1x + 30:
						if bulletY >= self.player1y - 20 and bulletY <= self.player1y + 20:
							if b in self.bullets:
									self.bullets.remove(b)
							self.player1health -=1
							if self.player1health == 0:
								self.player1alive = 0
								self.player1DeadTime = time.time()
							continue

				if bulletX <= 0 or bulletY <= 0 or bulletX >= 650 or bulletY >= 450:
					if b in self.bullets:
						self.bullets.remove(b)
		#Move bullets
		if( events["mouseEvent"] == 'Pressed' and self.player2alive):
			self.bullets.append( BulletData(self.IDcount, 2, self.player2x, self.player2y, self.r2Angle, self.gunLength))
			self.IDcount+=1

		for e in self.enemies:
			if self.player1alive and self.player2alive:
				e.setTarget(self.player1x, self.player1y, self.player2x, self.player2y)
			elif self.player1alive:
				e.target = 1
			elif self.player2alive:
				e.target = 2
			if(e.target == 2 and e.alive == 1):
				e.move(self.player2x, self.player2y)
				if(random.randrange(0,100,1) == 1):
					if self.player2alive:
						self.enemyFire(e.getPos(),2,3)
		

		self.sendGameData(2)
		return

	def movePlayer(self, playerID, direction):
		if(direction == 'Right'):
			if playerID == 1:
				if self.player1x < 622:
					self.player1x = self.player1x + 1
					self.player1Angle = 90
			if playerID == 2:
				if self.player2x < 622:
					self.player2x = self.player2x + 1
					self.player2Angle = 90

		if(direction == 'Left'):
			if playerID == 1:
				if self.player1x > 28:
					self.player1x = self.player1x - 1
					self.player1Angle = 270
			if playerID == 2:
				if self.player2x > 28:
					self.player2x = self.player2x - 1
					self.player2Angle = 270

		if(direction == 'Up'):
			if playerID == 1:
				if self.player1y > 15:
					self.player1y = self.player1y - 1
					self.player1Angle = 180
			if playerID == 2:
				if self.player2y > 15:
					self.player2y = self.player2y - 1
					self.player2Angle = 180

		if(direction == 'Down'):
			if playerID == 1:
				if self.player1y < 485:
					self.player1y = self.player1y + 1
					self.player1Angle = 0
			if playerID == 2:
				if self.player2y < 485:
					self.player2y = self.player2y + 1
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

	def enemyFire(self,enemyPos,playerID,bID):
		enemyX,enemyY = enemyPos
		if playerID == 1:
			dx = self.player1x - enemyX
			dy = self.player1y - enemyY
		else:
			dx = self.player2x - enemyX
			dy = self.player2y - enemyY
		angle = atan2(dy, -dx)

		self.bullets.append(BulletData(self.IDcount, playerID, enemyX, enemyY, angle, self.gunLength,bID))
		self.IDcount += 1

	def sendGameData(self, playerID):

		data = {}
		data['player1x'] = self.player1x
		data['player1y'] = self.player1y
		data['player2x'] = self.player2x
		data['player2y'] = self.player2y
		data['player1alive'] = self.player1alive
		data['player2alive'] = self.player2alive
		data['exit'] = 0
		data['time'] = int(round(self.timer - (time.time() - self.startTime)))

		if(playerID == 1):
			data['partnerGunAngle'] = self.player2GunAngle
			data['kills'] = self.player1Kills
		if(playerID == 2):
			data['partnerGunAngle'] = self.player1GunAngle
			data['kills'] = self.player2Kills

		data['player1Angle'] = self.player1Angle
		data['player2Angle'] = self.player2Angle

		data['enemies'] = []
		for e in self.enemies:
			data['enemies'].append({'enemyID' : e.enemyID, 'x':e.xcenter, 'y':e.ycenter, 'angle':e.angle})
		data['bullets'] = []
		for b in self.bullets:
			data['bullets'].append({'bulletID' : b.bulletID, 'x':b.xcenter, 'y':b.ycenter, 'angle':b.angle,'playerID':b.playerID})

		data['player1Health'] = self.player1health
		data['player2Health'] = self.player2health
				
		data = json.dumps(data)
		if playerID == 1:
			self.player1Connection.transport.write(data)
		if playerID == 2:
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

