import sys
import os

from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred

import pygame
from pygame.locals import *
from math import atan2, degrees, pi
from math import *

import cPickle as pickle

class EventPackage:
	def __init__(self, connection):
		self.handler = {}
		self.handler['keyEvents'] = ""
		self.handler['mouseEvents'] = ""
		self.handler['mx'] = ""
		self.handler['my'] = ""
		self.connection = connection

	def addKeyEvent(self,event):
		if keycode == K_RIGHT:
			self.handler['keyEvents'] = "Right"
		if keycode == K_LEFT:
			self.handler['keyEvents'] = "Left"
		if keycode == K_UP:
			self.handler['keyEvents'] = "Up"
		if keycode == K_DOWN:
			self.handler['keyEvents'] = "Down"		

	def addMouseEvents(self,event, mx, my):
		self.handler['mouseEvents'] = "Pressed"
		self.handler['mx'] = mx
		self.handler['my'] = my

	def send(self):
		data = pickle.load(self.handler)
		self.connection.transport.write(data)

class Player1(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("Hutchkiss.png")
		self.rect = self.image.get_rect()

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
		self.x = 300
		self.y = 300

	def tick(self):
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, 270)
		self.rect = self.image.get_rect(center=center)

class Gun(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("HutchkissGunMM.png")
		self.rect = self.image.get_rect()
		# keep original image to limit resize errors
		self.orig_image = self.image
		self.rect.x += 7
		self.rect.y += 5

	def tick(self):
		if (playerID == 1):
			# get the mouse x and y position on the screen
			center = self.rect.center
			if (pygame.mouse.get_focused()):
				mx, my = pygame.mouse.get_pos()
				dx = mx - (self.rect.x + (self.image.get_width()/2))
				dy = my - (self.rect.y + (self.image.get_height()/2))
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
		self.image = pygame.image.load("PaznerGunMM.png")
		self.rect = self.image.get_rect()
		# keep original image to limit resize errors
		self.orig_image = self.image
		self.rect.x += 307
		self.rect.y += 305

	def tick(self):
		if (playerID == 2):
			# get the mouse x and y position on the screen
			center = self.rect.center
			if (pygame.mouse.get_focused()):
				mx, my = pygame.mouse.get_pos()
				dx = mx - (self.rect.x + (self.image.get_width()/2))
				dy = my - (self.rect.y + (self.image.get_height()/2))
				rAngle = atan2(dy, -dx)
				dAngle  = degrees(rAngle) + 90
			else:
				dAngle = 270
			

class GameSpace:
        def __init__(self,connection, playerID):
		self.connection = connection
		self.playerID = playerID

	def main(self):
		# 1) basic initialization
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		self.enemyHealth = 3
		# 2) set up game objects
		self.clock = pygame.time.Clock()
		self.Gun = Gun(self)
		self.Player = Player(self)
		self.Gun2 = Gun(self)
		self.Player2 = Player(self)
		check2 = True
		pickle = EventPackage(self.connection)
		# 3) start game loop
		while 1:
			# 4) clock tick regulation (framerate)
			check = True				
			self.clock.tick(60)
			self.screen.fill(self.black)
			# 5) this is where you would handle user inputs...
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					pickle.addKeyEvent(event.key)
				if event.type == MOUSEBUTTONDOWN:
					#Add mouse event to event dictionary	
					#Add mouse coordinates to event dictionary
					mx, my = pygame.mouse.get_pos()
					pickle.addMouseEvent(event.key, mx, my)
				if event.type == pygame.QUIT:
					sys.exit()
			pickle.send()
			# 6) send a tick to every game object!
			self.Gun.tick()
			self.Player.tick()
			# 7) and finally, display the game objects
			self.screen.blit(self.Player.image, self.Player.rect)
			self.screen.blit(self.Gun.image, self.Gun.rect)
			self.screen.blit(self.Player2.image, self.Player2.rect)
			self.screen.blit(self.Gun2.image, self.Gun2.rect)
			pygame.display.flip()
