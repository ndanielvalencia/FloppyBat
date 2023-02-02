#   Nelson D Valencia
        #   ​CSCI 101 – Section C
        #   CREATE PROJECT
        #   "Floppy the Bat!" 

# --First off, credits where credits are due.--

# 1. Thanks to Ahmet Avci for the 8-bit bat graphics used for this game. His patreon link is https://www.patreon.com/elthen

# 2. Also thanks to opengameart.org and freesound.org for some of the open source graphics and audio files used for this game

# 3. Thanks for Tech with Tim for providing a series of comprehensive youtube tutorial videos that guided me through the process of 
#    coding this project and helped me understand the pygame module. 
#    Link to his channel is https://www.youtube.com/channel/UC4JX40jDee_tINbkjycV4Sg.

# 4. And thanks to ALL the Computer science department at Colorado School of Mines for teaching me how to program in Python and their immense support!

import pygame
import time
import os
import random

# Initializing the pygame font and mixer module

pygame.font.init()
pygame.mixer.pre_init(22050, -16, 2, 1024)
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(22050, -16, 2, 1024)

# Constants to set screen size and title

WINDOW_WIDTH = 560 
WINDOW_HEIGHT = 800
pygame.display.set_caption("Floppy Bat")

# importing game resources (images and sounds)

BACKGROUND = pygame.transform.scale2x(pygame.image.load('bg.png'))
PIPE = pygame.transform.scale2x(pygame.image.load('pipe.png'))
GROUND = pygame.transform.scale2x(pygame.image.load('ground.png'))
GAMEOVER = pygame.image.load('gameover.png')
PRESSKEY = pygame.image.load('presskey.png')

# Storing several sprites as a list keeps the code cleaner

BAT_SPRITES = [ 
	pygame.transform.scale2x(pygame.image.load('bat1.png')),
	pygame.transform.scale2x(pygame.image.load('bat2.png')),
	pygame.transform.scale2x(pygame.image.load('bat3.png')),
	pygame.transform.scale2x(pygame.image.load('bat4.png')),
	pygame.transform.scale2x(pygame.image.load('bat5.png'))
	]


GAME_SOUNDS = {}
GAME_SOUNDS['flap'] = pygame.mixer.Sound('flap.wav')

#This will be the font used to display the player's current score

SCORE_FONT = pygame.font.SysFont("impact", 60)

# Game elements

class Bat:

	SPRITES = BAT_SPRITES # Accesses the bat sprites list
	ANIMATION_TIME = 4 # How fast the animation displays
	ROTATION_VELOCITY = 20  # Velocity at which the bat rotates
	MAX_ROTATION = 25  # Max degree at which the bat rotates
	

	def __init__(self, x, y):

		self.x = x 
		self.y = y 
		self.height = self.y
		self.tick_count = 0
		self.velocity = 0
		self.tilt = 0
		self.sprite = self.SPRITES[0]
		self.sprite_count = 0

	def jump(self): # The jump function for our bat

		self.velocity = -10 # If we want velocity to be upwards, this value must be negative
		self.tick_count = 0 # keeps track of our last jump
		self.height = self.y # Keeps track of where the bat last jumped from

	def move(self): # Handles the physics of our bat

		self.tick_count += 1 # Keeps track of how many times it moved since it last jumped

		displacement = self.velocity * self.tick_count + 1.3 * self.tick_count ** 2 # Can be translated to freefall physics equation with tick_count as time

		if displacement < 0:
			displacement -= 5 # A little boost upwards

		if displacement >= 15: # When downwards displacement is too big, change value to 15 and keep it constant
			displacement =  15

		self.y = self.y + displacement

		if self.y < 0: # Stops bat from moving out of the screen boundary
			self.y = 0

		if self.y > 685: #When bat falls to the ground, keeps it there
			self.y = 685

		if displacement < 0 or self.y < self.height + 50:

			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION # If bat is going upwards, inmediately change its tilt to max rotation degree

		else: 
			if self.tilt > -90:
				self.tilt -= self.ROTATION_VELOCITY # Tilts bat down nicely

	def draw(self, win):  # Time to animate our bat!

		self.sprite_count += 1

		if self.sprite_count < self.ANIMATION_TIME: #This code changes sprite of bat depending on animation time

			self.sprite = self.SPRITES[0]

		elif self.sprite_count < self.ANIMATION_TIME * 2:

			self.sprite = self.SPRITES[1]

		elif self.sprite_count < self.ANIMATION_TIME * 3:

			self.sprite = self.SPRITES[2]

		elif self.sprite_count < self.ANIMATION_TIME * 4:

			self.sprite = self.SPRITES[3]

		elif self.sprite_count < self.ANIMATION_TIME * 5:

			self.sprite = self.SPRITES[4]
			self.sprite_count = 0

		if self.tilt <= -80 or dead: # Stops animation when bat is diving down or if dead

			self.sprite = self.SPRITES[1]
			self.sprite_count = self.ANIMATION_TIME * 2
			
		rotated_image = pygame.transform.rotate(self.sprite, self.tilt) # This piece of code rotates the bat sprite around the center, basically sets the anchor point
		new_rect = rotated_image.get_rect(center = self.sprite.get_rect(topleft = (int(self.x), int(self.y))).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self): # Function used to get a mask for our bat sprite collision detection

		return pygame.mask.from_surface(self.sprite)

class GameOver: # Gameover and "press key to continue" screens here

	SCREEN = GAMEOVER
	SCREEN2 = PRESSKEY
	global dead

	def __init__(self, x, y):

		self.x = x
		self.y = y

	def draw(self, win):

		if dead:

			win.blit(self.SCREEN, (self.x, self.y)) # Displays gameover screen if player collides or falls to the ground

		if presskey: 

			win.blit(self.SCREEN2, (self.x, self.y)) # Displays the press key screen ONLY if player falls to the ground

class Pipe:

	VELOCITY = 5 # Pipes move to the left of the screen, giving the illusion to the player that the bat is moving
	GAP = 200 # Gap between pipes


	def __init__(self, x):

		self.x = x
		self.height = 0
		self.top = 0 # Variables to keep track of where the pipes will be drawn
		self.bottom = 0 
		self.PIPE_BOTTOM = PIPE
		self.PIPE_TOP = pygame.transform.flip(PIPE, False, True) # Flips the image for the top pipe
		self.passed = False

		self.set_height()

	def set_height(self):

		self.height = random.randrange(50, 500) #This is the function in charge of randomizing the length of the pipes
		self.top = self.height - self.PIPE_TOP.get_height() # Defines the coordinates at which the top pipe will be drawn on screen
		self.bottom = self.height + self.GAP # Same, but for bottom pipe

	def move(self):

		self.x -= self.VELOCITY # Moves pipe to the left

	def collide (self, bat):

		bat_mask = bat.get_mask() # This function makes a mask of all non-transparent pixels of our bat
		top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP) # Same but for top pipe
		bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # ... and bottom pipe

		top_offset = (self.x - bat.x, self.top - round(bat.y)) # Round functions need to be used as there cannot be decimals in this function
		bottom_offset = (self.x - bat.x, self.bottom - round(bat.y))

		bottom_point = bat_mask.overlap(bottom_pipe_mask, bottom_offset) # Checks if bat pixels overlap pipes pixels
		top_point = bat_mask.overlap(top_pipe_mask, top_offset)

		if top_point or bottom_point: # Checks if pixel collision occurs
			return True 

		return False 

	def draw(self, win):

		win.blit(self.PIPE_TOP, (self.x, self.top)) # Draws pipes, very self explanatory
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

class Ground:

	VELOCITY = 5 # Same as pipes, the ground is constantly moving to the left.
	WIDTH = GROUND.get_width()
	IMAGE = GROUND

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH 

	def move(self): # This code displays 2 ground graphics attached to each other moving continously to the left to make the illusion of the bat moving across the screen
		self.x1 -= self.VELOCITY
		self.x2 -= self.VELOCITY

		if self.x1 + self.WIDTH < 0: # Conditional statements to make the grounds graphics automatically reappear to the right of the screen once it finishes moving all the way to the left
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win): 

		win.blit(self.IMAGE, (self.x1, self.y))
		win.blit(self.IMAGE, (self.x2, self.y))

def draw_window(win, bat, pipes, ground, score, gameover):
	win.blit(BACKGROUND, (0,-70)) # Displays the background

	for pipe in pipes:

		pipe.draw(win)

	text = SCORE_FONT.render(str(score), 1, (255, 255, 255)) # Time to draw our score on screen
	win.blit(text, (round(WINDOW_WIDTH / 2) - 10, 15))

	ground.draw(win) # And the ground ...
	bat.draw(win) # And the bat ....
	gameover.draw(win) # Only draws the gameover screen when player "dies"

	pygame.display.update()

def main():

	bat = Bat(260, 300) # Coordinates to display our game's elements
	ground = Ground(700)
	pipes = [Pipe(560)]
	gameover = GameOver(0,0)
	clock = pygame.time.Clock()

	win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Setting our window display

	# Variables that need to be restarted if player decides to play again

	global score
	score = 0
	global dead
	dead = False
	global run
	run = True
	global presskey
	presskey = False
	global ismoving
	ismoving = False

	#This will define the frame rate of the game and run the framework

	while run:

		clock.tick(30)

		for event in pygame.event.get():

			if event.type == pygame.KEYDOWN:

				if event.key == pygame.K_ESCAPE: # If escape key pressed, ends the game

					 run = False

				elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN): # If any other key pressed, bat jumps.

					if not dead:

						bat.jump()
						ismoving = True # Ensures bat starts moving after our first key press and doesn't automatically fall to the ground when starting the game
						GAME_SOUNDS['flap'].play() 							

					elif bat.y + bat.sprite.get_height() >= 680 or not ismoving: # Restarts the game when we lose

						main()
					
			if event.type == pygame.QUIT: # Quits pygame when pressing the 'x' button

				run = False 

		add_pipe = False
		remove = [] # List of removed pipes

		for pipe in pipes:

			if pipe.collide(bat):

				dead = True # Kills our bat

				if not ismoving:

					presskey = True # If we don't press any key, inmediately displays our "Press key to continue" screen

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: # Generates another pipe when current one goes offscreen

				remove.append(pipe)

			if not pipe.passed and pipe.x < bat.x: # When player bypasses a pair of pipes, commands game to add another pair of pipes

				pipe.passed = True
				add_pipe = True

			if not dead:

				pipe.move() # Moves pipes as long as the bat is alive.

		if add_pipe:

			pipes.append(Pipe(560)) # Displays another pipe

			if not dead:

				score += 1

		for element in remove:

			pipes.remove(element) # Removes pipes already passed 

		if bat.y + bat.sprite.get_height() >= 685: # Kills the bat if it hits the ground:

			dead = True
			presskey = True

		if ismoving:

			bat.move() # Only starts freefall physics for our bat after our first keypress

		if not dead:

			ground.move() # Stops the ground if our bat dies

		draw_window(win, bat, pipes, ground, score, gameover) # Draws all of our games elements on the window at the same time

	pygame.quit()
	quit()

main() #Initializes our game!

