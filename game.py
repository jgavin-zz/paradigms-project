import sys
import os

from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred
from twisted.internet import task

import pygame
from pygame.locals import *
from math import atan2, degrees, pi
from math import *

import cPickle as pickle
import json
import time

class EventPackage:
	def __init__(self, connection):
		self.handler = {}
		self.handler['keyPressed'] = ""
		self.handler['mouseEvent'] = ""
		self.handler['mx'] = ""
		self.handler['my'] = ""
		self.handler['exit'] = "0"
		self.handler['restart'] = "0"
		self.connection = connection

	def addKeyEvent(self, keycode):
		if keycode == K_d:
			self.handler['keyPressed'] = "Right"
		if keycode == K_a:
			self.handler['keyPressed'] = "Left"
		if keycode == K_w:
			self.handler['keyPressed'] = "Up"
		if keycode == K_s:
			self.handler['keyPressed'] = "Down"		

	def setMousePressed(self):
		self.handler['mouseEvent'] = "Pressed"

	def setMouseCoordinates(self, mx, my):
		self.handler['mx'] = mx
		self.handler['my'] = my

	def setExit(self):
		self.handler['exit'] = "1"

	def restart(self):
		self.handler['restart'] = "1"

	def send(self):
		data = json.dumps(self.handler)
		self.connection.transport.write(data)

class Background(pygame.sprite.Sprite):
	def __init__(self, image_name):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(image_name)
		self.image = pygame.transform.scale(self.image, (650, 500))
		self.rect = self.image.get_rect()


class Player1(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("Hutchkiss.jpg")
		self.rect = self.image.get_rect()
		self.orig_image = self.image

	def tick(self):
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, 270)
		self.rect = self.image.get_rect(center=center)	

class Player2(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("Panzer.jpg")
		self.rect = self.image.get_rect()
		self.orig_image = self.image

	def tick(self):
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, 270)
		self.rect = self.image.get_rect(center=center)

class Gun1(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("HutchkissGunMM.png")
		self.rect = self.image.get_rect()
		# keep original image to limit resize errors
		self.orig_image = self.image

	def tick(self):
		if (self.gs.playerID == 1):
			# get the mouse x and y position on the screen
			center = self.rect.center
			if (pygame.mouse.get_focused()):
				mx, my = pygame.mouse.get_pos()
				dx = mx - (self.rect.centerx)
				dy = my - (self.rect.centery)
				rAngle = atan2(dy, -dx)
				dAngle  = degrees(rAngle) + 90
			else:
				dAngle = 270
			self.image = pygame.transform.rotate(self.orig_image, dAngle)
			self.rect = self.image.get_rect(center=center)	

	
class Gun2(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("PanzerGunMM.png")
		self.rect = self.image.get_rect()
		# keep original image to limit resize errors
		self.orig_image = self.image

	def tick(self):
		if (self.gs.playerID == 2):
			# get the mouse x and y position on the screen
			center = self.rect.center
			if (pygame.mouse.get_focused()):
				mx, my = pygame.mouse.get_pos()
				dx = mx - (self.rect.centerx)
				dy = my - (self.rect.centery)
				rAngle = atan2(dy, -dx)
				dAngle  = degrees(rAngle) + 90
			else:
				dAngle = 270
			self.image = pygame.transform.rotate(self.orig_image, dAngle)
			self.rect = self.image.get_rect(center=center)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, angle, ID, img):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img)
		self.image = pygame.transform.scale(self.image, (10, 10))
		self.orig_image = self.image
		self.rect = self.image.get_rect()
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, angle)
		self.rect = self.image.get_rect(center=center)
		self.rect.centerx = x
		self.rect.centery = y
		self.ID = ID
		# keep original image to limit resize errors

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y, angle,ID):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("soldier.jpg")
		self.image = pygame.transform.scale(self.image, (20, 40))
		self.orig_image = self.image
		self.rect = self.image.get_rect()
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, angle)
		self.rect = self.image.get_rect(center=center)
		self.rect.centerx = x
		self.rect.centery = y	
		self.ID = ID

class Healthbar(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("healthBar.jpg")
		self.image = pygame.transform.scale(self.image, (200, 10))
		self.orig_width = 200
		self.orig_image = self.image
		self.rect = self.image.get_rect()
		self.orig_x = x
		self.orig_y = y
		self.rect.x = x
		self.rect.y = y

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, life):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("explosion.png")
		self.image = pygame.transform.scale(self.image, (20, 20))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.life = life

class GameSpace:

	#Initiale game space with connection and playerID number
        def __init__(self, handler):

		self.connection = handler.connection
		self.playerID = handler.playerID
		self.handler = handler
		self.playerKills = 0
		self.timer = 60

	def updateGameData(self, data):
		bulletID = []
		enemyID = []
		#Update Player Positions
		self.Player1.rect.centerx = data['player1x']
		self.Player1.rect.centery = data['player1y']
		self.Player2.rect.centerx = data['player2x']
		self.Player2.rect.centery = data['player2y']

		#Update Gun Positions
		self.Gun1.rect.centerx = data['player1x']
		self.Gun1.rect.centery = data['player1y']
		self.Gun2.rect.centerx = data['player2x']
		self.Gun2.rect.centery = data['player2y']

		self.playerKills = data['kills']
		self.timer = data['time']

		#Update Partner Gun Angle
		angle = data['partnerGunAngle']
		if(self.playerID == 1):
			self.Gun2.image = pygame.transform.rotate(self.Gun2.orig_image, angle)
			center = self.Gun2.rect.center
			self.Gun2.rect = self.Gun2.image.get_rect(center=center)
		if(self.playerID == 2):
			self.Gun1.image = pygame.transform.rotate(self.Gun1.orig_image, angle)
			center = self.Gun1.rect.center
			self.Gun1.rect = self.Gun1.image.get_rect(center=center)

		#Update Player Angles
		angle = data['player1Angle']
		self.Player1.image = pygame.transform.rotate(self.Player1.orig_image, angle)
		center = self.Player1.rect.center
		self.Player1.rect = self.Player1.image.get_rect(center=center)
		angle = data['player2Angle']
		self.Player2.image = pygame.transform.rotate(self.Player2.orig_image, angle)
		center = self.Player2.rect.center
		self.Player2.rect = self.Player2.image.get_rect(center=center)

		#Update Bullets
		for b in data['bullets']:
			bulletID.append(b['bulletID'])
			check = 1
			for l in self.bullets:
				if b['bulletID'] == l.ID:
					l.rect.centerx = b['x']
					l.rect.centery = b['y']
					check = 0
			if check:
				if(b['type'] == 1):
					self.bullets.append(Bullet(b['x'], b['y'], b['angle'], b['bulletID'], "blueBullet.jpg"))
				if(b['type'] == 2):
					self.bullets.append(Bullet(b['x'], b['y'], b['angle'], b['bulletID'], "greenBullet.png"))	
				if(b['type'] == 3):
					self.bullets.append(Bullet(b['x'], b['y'], b['angle'], b['bulletID'], "redBullet.png"))		 

		for b in self.bullets:
			if b.ID not in bulletID:
				self.bullets.remove(b) 

		#Update Enemies
		for e in data['enemies']:
			enemyID.append(e['enemyID'])
			check = 1
			for l in self.enemies:
				if e['enemyID'] == l.ID:
					l.rect.centerx = e['x']
					l.rect.centery = e['y']
					l.image = pygame.transform.rotate(l.orig_image, e['angle'])
					center = l.rect.center
					l.rect = l.image.get_rect(center=center)
					check = 0
			if check:
				self.enemies.append(Enemy(e['x'], e['y'], e['angle'], e['enemyID']))	
		
		for e in self.enemies:
			if e.ID not in enemyID:
				self.enemies.remove(e) 

		#Update health bar
		self.player1Health = data['player1Health']
		r1 = float(self.player1Health) / 10
		new_width1 = int(self.player1HealthBar.orig_width * r1)
		self.player1HealthBar.image = pygame.transform.scale(self.player1HealthBar.orig_image, (new_width1, 10))
		self.player1HealthBar.rect = self.player1HealthBar.image.get_rect()
		self.player1HealthBar.rect.x = self.player1HealthBar.orig_x
		self.player1HealthBar.rect.y = self.player1HealthBar.orig_y

		self.player2Health = data['player2Health']
		r2 = float(self.player2Health) / 10
		new_width2 = int(self.player2HealthBar.orig_width * r2)
		self.player2HealthBar.image = pygame.transform.scale(self.player2HealthBar.orig_image, (new_width2, 10))
		self.player2HealthBar.rect = self.player2HealthBar.image.get_rect()
		self.player2HealthBar.rect.x = self.player2HealthBar.orig_x
		self.player2HealthBar.rect.y = self.player2HealthBar.orig_y

		#Update explosions
		for e in self.explosions:
			e.life = e.life - 1
			if(e.life == 0):
				self.explosions.remove(e)
		for e in data['explosions']:
			self.explosions.append(Explosion(e['x'], e['y'], 10))

		#Update Sounds
		self.playGunSound = data['gunSound']
		self.playHitSound = data['hitSound']
		self.playSquashSound = data['squashSound']
		
	def startScreen(self,handler,Type):
		self.connection = handler.connection
		self.playerID = handler.playerID
		self.handler = handler
		self.event_package = EventPackage(self.connection)
		#Initialize basic game information
		pygame.init()
		self.size = self.width, self.height = 650, 500
		self.black = 0, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Player " + str(self.playerID))
		self.screen.fill(self.black)
		#Initialize game objects
		self.background = Background("startscreen1.jpg")
		self.Player1 = Player1(self)
		self.Gun1 = Gun1(self)
		self.Player2 = Player2(self)
		self.Gun2 = Gun2(self)
		check2 = True
		if Type == 2:	
			self.background = Background("startscreen2.jpg")
		self.screen.blit(self.background.image, self.background.rect)	
		if self.playerID == 1:
			self.Player1.rect.centerx = 100
			self.Player1.rect.centery = 100
			self.Gun1.rect.centerx = 100
			self.Gun1.rect.centery = 100
			self.Gun1.image = pygame.transform.rotate(self.Gun1.orig_image, 270)
			center = self.Gun1.rect.center
			self.Gun1.rect = self.Gun1.image.get_rect(center=center)
			self.Player1.image = pygame.transform.rotate(self.Player1.orig_image, 90)
			center = self.Player1.rect.center
			self.Player1.rect = self.Player1.image.get_rect(center=center)
			self.screen.blit(self.Player1.image, self.Player1.rect)
			self.screen.blit(self.Gun1.image, self.Gun1.rect)
		else:
			self.Player2.rect.centerx = 200
			self.Player2.rect.centery = 200
			self.Gun2.rect.centerx = 200
			self.Gun2.rect.centery = 200
			self.Gun2.image = pygame.transform.rotate(self.Gun2.orig_image, 270)
			center = self.Gun2.rect.center
			self.Gun2.rect = self.Gun2.image.get_rect(center=center)
			self.Player2.image = pygame.transform.rotate(self.Player2.orig_image, 90)
			center = self.Player2.rect.center
			self.Player2.rect = self.Player2.image.get_rect(center=center)
			self.screen.blit(self.Player2.image, self.Player2.rect)
			self.screen.blit(self.Gun2.image, self.Gun2.rect)
		pygame.display.flip()	
		if Type == 1:
			while 1:
				for event in pygame.event.get():
					if event.type == MOUSEBUTTONDOWN:
						mx,my = pygame.mouse.get_pos()
						if (mx > 175 and mx < 475 and my > 210 and my < 310):
							self.connection.transport.write("Clicked")
							return
					if event.type == pygame.QUIT:
						self.event_package.setExit()
						pygame.quit()
						self.event_package.send()
						return


	#Main function which drives gameplay
	def main(self,handler):
		self.background = Background("desert-texture.jpg")
		self.connection = handler.connection
		self.playerID = handler.playerID
		self.handler = handler
		self.bullets = []
		self.enemies = []
		self.explosions = []
		self.player1HealthBar = Healthbar(25, 35)
		self.player2HealthBar = Healthbar(425, 35)
		self.gunSound = pygame.mixer.Sound('gunSound.ogg')
		self.playGunSound = 0
		self.hitSound = pygame.mixer.Sound('hitSound.ogg')
		self.playHitSound = 0
		self.squashSound = pygame.mixer.Sound('squashSound.ogg')
		self.playSquashSound = 0
		self.font = pygame.font.SysFont("monospace",15)
		self.player1tag = self.font.render("Player 1", 1, (255,255,0))
		self.p1rect = self.player1tag.get_rect()
		self.p1rect.centerx = 125
		self.p1rect.centery = 25
		self.player2tag = self.font.render("Player 2", 1, (255,255,0))
		self.p2rect = self.player2tag.get_rect()
		self.p2rect.centerx = 525
		self.p2rect.centery = 25
		self.kill = self.font.render("Kills:", 1, (255,255,0))
		self.killRect = self.kill.get_rect()
		self.killRect.centerx = 315
		self.killRect.centery = 20
		self.time = self.font.render("Time:", 1, (255,255,0))
		self.timeRect = self.time.get_rect()
		self.timeRect.centerx = 319
		self.timeRect.centery = 20
		pygame.key.set_repeat(1, 500)
		#Initiate game loop
		self.lc = task.LoopingCall(self.gameLoop)
		self.lc.start(.01)

	def gameOver(self,winner):
		if (winner == 1):
			self.background = Background("endscreen1.png")
		else:
			self.background = Background("endscreen2.png")
		self.screen.blit(self.background.image, self.background.rect)	
		pygame.display.flip()
		while 1:
			for event in pygame.event.get():
					if event.type == MOUSEBUTTONDOWN:
						mx,my = pygame.mouse.get_pos()
						if (mx > 160 and mx < 485 and my > 260 and my < 350):
							self.handler.gameData['restart'] = 1
							self.event_package.restart()
							self.event_package.send()
							self.lc.stop()
							return
					if event.type == pygame.QUIT:
						self.event_package.setExit()
						pygame.quit()
						self.event_package.send()
						self.lc.stop()
						return

	def gameLoop(self):

		#Get game info from server and update object information
		newData = self.handler.gameData
		if newData['time'] == 0:
			self.gameOver(newData['winner'])
			return
		self.updateGameData(newData)
		check = 0
		#Add user input events to event package and send package to server
		self.event_package = EventPackage(self.connection)
		for event in pygame.event.get():
			if event.type == MOUSEBUTTONDOWN:
				self.event_package.setMousePressed()
			if event.type == pygame.QUIT:
				self.event_package.setExit()
				pygame.quit()
				self.event_package.send()
				return

		keys = pygame.key.get_pressed()
		if(keys[K_a]):
			self.event_package.addKeyEvent(K_a)
		if(keys[K_w]):
			self.event_package.addKeyEvent(K_w)
		if(keys[K_s]):
			self.event_package.addKeyEvent(K_s)
		if(keys[K_d]):
			self.event_package.addKeyEvent(K_d)
	
	
		mx, my = pygame.mouse.get_pos()
		self.event_package.setMouseCoordinates(mx, my)
		self.event_package.send()


		#Send ticks to objects
		if newData['player1alive']:
			self.Gun1.tick()
			self.Player1.tick()
		if newData['player2alive']:
			self.Player2.tick()
			self.Gun2.tick()

		#Blit objects to screen
		self.screen.fill(self.black)
		self.screen.blit(self.background.image, self.background.rect)
		self.screen.blit(self.kill,self.killRect)
		self.screen.blit(self.time,self.timeRect)
		self.screen.blit(self.player1tag, self.p1rect)
		self.screen.blit(self.player2tag, self.p2rect)
		self.killCount = self.font.render(str(self.playerKills),1,(255,255,0))
		self.countRect = self.killCount.get_rect()
		self.countRect.centerx = 350
		self.countRect.centery = 50
		self.screen.blit(self.killCount,self.countRect)
		self.timeCount = self.font.render(str(self.timer),1,(255,255,0))
		self.tCountRect = self.timeCount.get_rect()
		self.tCountRect.centerx = 350
		self.tCountRect.centery = 30
		self.screen.blit(self.timeCount,self.tCountRect)
		if newData['player1alive']:
			self.screen.blit(self.Player1.image, self.Player1.rect)
			self.screen.blit(self.Gun1.image, self.Gun1.rect)
		if newData['player2alive']:
			self.screen.blit(self.Player2.image, self.Player2.rect)
			self.screen.blit(self.Gun2.image, self.Gun2.rect)
		for b in self.bullets:
			self.screen.blit(b.image, b.rect)
		for e in self.enemies:
			self.screen.blit(e.image, e.rect)
		for e in self.explosions:
			self.screen.blit(e.image, e.rect)
		self.screen.blit(self.player1HealthBar.image, self.player1HealthBar.rect)
		self.screen.blit(self.player2HealthBar.image, self.player2HealthBar.rect)

		#Play Sounds
		if(self.playGunSound):
			self.gunSound.play()
		if(self.playHitSound):
			self.hitSound.play()
		if(self.playSquashSound):
			self.squashSound.play()

		pygame.display.flip()
