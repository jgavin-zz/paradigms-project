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

class EventPackage:
	def __init__(self, connection):
		self.handler = {}
		self.handler['keyPressed'] = ""
		self.handler['mouseEvent'] = ""
		self.handler['mx'] = ""
		self.handler['my'] = ""
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

	def send(self):
		data = json.dumps(self.handler)
		self.connection.transport.write(data)

class Background(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("desert-texture.jpg")
		self.rect = self.image.get_rect()


class Player1(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("Hutchkiss.png")
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
		self.image = pygame.image.load("Panzer.png")
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
			

class GameSpace:

	#Initiale game space with connection and playerID number
        def __init__(self, handler):

		self.connection = handler.connection
		self.playerID = handler.playerID
		self.handler = handler

	
	def updateGameData(self, data):

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
		
		
		


	#Main function which drives gameplay
	def main(self):

		#Initialize basic game information
		pygame.init()
		self.size = self.width, self.height = 400, 300
		self.black = 0, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Player " + str(self.playerID))

		#Initialize game objects
		self.background = Background(self)
		self.Player1 = Player1(self)
		self.Gun1 = Gun1(self)
		self.Player2 = Player2(self)
		self.Gun2 = Gun2(self)
		check2 = True

		pygame.key.set_repeat()
		#Initiate game loop
		lc = task.LoopingCall(self.gameLoop)
		lc.start(.01)

	def gameLoop(self):

		#Get game info from server and update object information
		newData = self.handler.gameData
		self.updateGameData(newData)

		#Add user input events to event package and send package to server
		self.event_package = EventPackage(self.connection)
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				self.event_package.addKeyEvent(event.key)
			if event.type == MOUSEBUTTONDOWN:
				self.event_package.setMousePressed()
			if event.type == pygame.QUIT:
				sys.exit()
		mx, my = pygame.mouse.get_pos()
		self.event_package.setMouseCoordinates(mx, my)
		self.event_package.send()


		#Send ticks to objects
		self.Gun1.tick()
		self.Gun2.tick()
		#self.Player1.tick()
		#self.Player2.tick()

		#Blit objects to screen
		self.screen.fill(self.black)
		self.screen.blit(self.background.image, self.background.rect)
		self.screen.blit(self.Player1.image, self.Player1.rect)
		self.screen.blit(self.Gun1.image, self.Gun1.rect)
		self.screen.blit(self.Player2.image, self.Player2.rect)
		self.screen.blit(self.Gun2.image, self.Gun2.rect)
		pygame.display.flip()
