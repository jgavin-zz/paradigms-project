import sys
import os

import pygame
from pygame.locals import *
from math import atan2, degrees, pi
import math

class Player(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("Panzer.png")
		self.rect = self.image.get_rect()
		# keep original image to limit resize errors
		self.orig_image = self.image
		# if I can fire laser beams, this flag will say
		# whether I should be firing them /right now/
		self.tofire = False

	def tick(self):
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, 270)
		self.rect = self.image.get_rect(center=center)	

	def move(self, keycode):
		if keycode == K_RIGHT:
			if self.rect.x + self.image.get_width() < 660:
				self.rect = self.rect.move(2, 0)
		if keycode == K_LEFT:
			if self.rect.x > -20:
				self.rect = self.rect.move(-2, 0)
		if keycode == K_UP:
			if self.rect.y > -20:
				self.rect = self.rect.move(0, -2)
		if keycode == K_DOWN:
			if self.rect.y + self.image.get_height() < 500:
				self.rect = self.rect.move(0, 2)
		return	

class Gun(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("PanzerGun.png")
		self.rect = self.image.get_rect()
		# keep original image to limit resize errors
		self.orig_image = self.image
		# if I can fire laser beams, this flag will say
		# whether I should be firing them /right now/
		self.tofire = False
		self.rect.x += 20
		#self.rect.center = (self.rect.center[0]-10,self.rect.center[1])

	def tick(self):
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
		new_pos = self.image.blit_pos.sub(10)
		self.rect = self.image.get_rect(center=center)		

	def move(self, keycode):
		if keycode == K_RIGHT:
			if self.rect.x + self.image.get_width() < 660:
				self.rect = self.rect.move(2, 0)
		if keycode == K_LEFT:
			if self.rect.x > -20:
				self.rect = self.rect.move(-2, 0)
		if keycode == K_UP:
			if self.rect.y > -20:
				self.rect = self.rect.move(0, -2)
		if keycode == K_DOWN:
			if self.rect.y + self.image.get_height() < 500:
				self.rect = self.rect.move(0, 2)
		return		
class Enemy(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("globe.png")
		self.rect = self.image.get_rect()
		self.rect.x = 300
		self.rect.y = 300

class Laser(pygame.sprite.Sprite):
	def __init__(self,  x, y, dAngle):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("laser.png")
		self.orig_image = self.image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		center = self.rect.center
		self.image = pygame.transform.rotate(self.orig_image, dAngle)
		self.rect = self.image.get_rect(center=center)

class GameSpace:
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
		self.enemy = Enemy(self)
		self.Player = Player(self)
		check2 = True
		# 3) start game loop
		while 1:
			# 4) clock tick regulation (framerate)
			check = True
			if check2:
				if self.enemyHealth > 0:
					self.enemy.image = pygame.image.load("globe.png")
				else:
					pygame.mixer.music.load('explode.wav')
					pygame.mixer.music.play(0)
					self.enemy.rect.x += 125
					for i in range(0,16):
						self.screen.fill(self.black)
						self.screen.blit(self.Player.image, self.Player.rect)
						self.screen.blit(self.Gun.image, self.Gun.rect)
						if i < 10:
							filename = "explosion/frames00" + str(i) + "a.png"
						else:
							filename = "explosion/frames0" + str(i) + "a.png"
						self.enemy.image = pygame.image.load(filename)
						self.screen.blit(self.enemy.image, self.enemy.rect)
						pygame.display.flip()
					check2 = False				
			self.clock.tick(60)
			self.screen.fill(self.black)
			# 5) this is where you would handle user inputs...
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					self.Gun.move(event.key)
					self.Player.move(event.key)
				if event.type == MOUSEBUTTONDOWN:
					pygame.mixer.music.load('screammachine.wav')
					pygame.mixer.music.play(0)
					mx, my = pygame.mouse.get_pos()
					xpos = float(self.Gun.rect.x + (self.Gun.image.get_width()/2))
					ypos = float(self.Gun.rect.y + (self.Gun.image.get_height()/2))
					dx = mx - xpos
					dy = my - ypos
					rAngle = atan2(-dy, dx)
					dAngle  = degrees(rAngle)
					while (xpos < self.width and ypos < self.height and xpos > 0  and ypos > 0):
						self.laser = Laser(xpos, ypos, dAngle)
				        	self.screen.blit(self.laser.image, self.laser.rect)
						cX = float((dx/self.laser.image.get_width()))/100
						cY = float((dy/self.laser.image.get_height()))/100
						xpos += cX
						ypos += cY
						if check2:
							if (xpos > 310 and ypos > 353):
								self.enemy.image = pygame.image.load("globe_red100.png")
								if check:
									self.enemyHealth -= 1
									check = False
				if event.type == pygame.QUIT:
					sys.exit()
			# 6) send a tick to every game object!
			self.Gun.tick()
			self.Player.tick()
			# 7) and finally, display the game objects
			self.screen.blit(self.Player.image, self.Player.rect)
			self.screen.blit(self.Gun.image, self.Gun.rect)
			self.screen.blit(self.enemy.image, self.enemy.rect)					
			pygame.display.flip()


if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
