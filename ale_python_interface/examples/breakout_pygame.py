
"""
Created on Wed Aug 10 14:55:30 2016

@author: logancross
"""

"""
A Simple Breakout Example
Paul Vincent Craven
"""

# --- Import libraries used for this program
# System libraries that come with python
import os, sys
import math
# Pygame library from http://www.pygame.org/
import pygame
from pygame.locals import *

# Define some colors
black = (0,0,0)
white = (255,255,255)
blue = (0,0,255)
green = (0,255,0)
red = (255,0,0)
purple = (0xBF,0x0F,0xB5)

# This function loads a sound
def load_sound(name):
   try:
       sound = pygame.mixer.Sound(name)
   except pygame.error, message:
       print 'Cannot load sound:', name
       raise SystemExit, message
   return sound

# This class represents each block that will get knocked out by the ball
# It derives from the "Sprite" class in Pygame
class Block(pygame.sprite.Sprite):
   # Constructor. Pass in the color of the block, and its x and y position
   def __init__(self,color,x,y,setspeed,setscore):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)
       # Class variables to hold the height and width of the block
       self.width=20
       self.height=15
       self.speed=setspeed
       self.score=setscore
       # Create the image of the block of appropriate size
       # The width and height are sent as a list for the first parameter.
       self.image = pygame.Surface([self.width, self.height])
       # Fill the image with the appropriate color
       self.image.fill(color)
       # Fetch the rectangle object that has the dimensions of the image
       self.rect = self.image.get_rect()
       # Move the top left of the rectangle to x,y.
       # This is where our block will appear..
       self.rect.topleft = (x,y)

# This class represents the ball        
# It derives from the "Sprite" class in Pygame
class Ball(pygame.sprite.Sprite):
   # Constructor. Pass in the color of the block, and its x and y position
   def __init__(self):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)
       # Class attributes for width and height
       self.width=10
       self.height=10
       self.speed=.2
       # A list with the x and y of our ball. (This is the starting position)
       self.mypos = ([0.0,180.0])
       # Direction in degrees (zero is straight up)
       self.direction=200
       # Speed in pixels per cycle
       self.speed=0.3
       # Create the image of the ball
       self.image = pygame.Surface([self.width, self.height])
       # Color the ball
       self.image.fill((white))
       # Get a rectangle object that shows where our image is
       self.rect = self.image.get_rect()
       # Get attributes for the height/width of the screen
       self.screenheight = pygame.display.get_surface().get_height()
       self.screenwidth = pygame.display.get_surface().get_width()

   # This function will bounce the ball off a horizontal surface (not a verticle one)
   def bounce(self,diff):
           self.direction = (180-self.direction)%360
           self.direction -= diff

   # Update the position of the ball
   def update(self):
       # Sine and Cosine work in degrees, so we have to convert them
       direction_radians = math.radians(self.direction)
       # Change the position (x and y) according to the speed and direction
       self.mypos[0] += self.speed * math.sin(direction_radians)
       self.mypos[1] -= self.speed * math.cos(direction_radians)
       # Update the rectangle of the ball so that it is at mypos
       self.rect.left=self.mypos[0]
       self.rect.top=self.mypos[1]
       # Do we bounce off the top of the screen?
       if self.mypos[1] <= 0:
           self.bounce(0)
           self.mypos[1]=1
       # Do we bounce off the left of the screen?
       if self.mypos[0] <= 0:
           self.direction = (360-self.direction)%360
           self.mypos[0]=1
       # Do we bounce of the right side of the screen?
       if self.mypos[0] > self.screenwidth-self.width:
           self.direction = (360-self.direction)%360
           self.mypos[0]=self.screenwidth-self.width-1

       if self.mypos[1] > 600:
           return True
       else:
           return False

# This class represents the bar at the bottom that the player controls
class Player(pygame.sprite.Sprite):
   # Constructor function
   def __init__(self):
       # Call the parent's constructor
       pygame.sprite.Sprite.__init__(self)

       self.width=75
       self.height=15
       self.image = pygame.Surface([self.width, self.height])
       self.image.fill((white))

       # Make our top-left corner the passed-in location.
       self.rect = self.image.get_rect()
       self.screenheight = pygame.display.get_surface().get_height()
       self.screenwidth = pygame.display.get_surface().get_width()
       print "Screen height",self.screenheight
       self.rect.topleft = (0,self.screenheight-self.height)

   # Update the player
   def update(self):
       # Get where the mouse is
       pos = pygame.mouse.get_pos()
       # Set the left side of the player bar to the mouse position
       self.rect.left = pos[0]
       # Make sure we don't push the player paddle off the right side of the screen
       if self.rect.left > self.screenwidth - self.width:
           self.rect.left = self.screenwidth - self.width

# This is the main function where our program begins
def main():
   score = 0
   # Call this function so the Pygame library can initialize itself
   pygame.init()
   # Create an 800x600 sized screen
   screen = pygame.display.set_mode([800, 600])
   # Set the title of the window
   pygame.display.set_caption('Breakout')
   # Enable this to make the mouse dissappear when over our window
   #pygame.mouse.set_visible(0)
   # This is a font we use to draw text on the screen (size 36)
   font = pygame.font.Font(None, 36)

   # Create a surface we can draw on
   background = pygame.Surface(screen.get_size())
   # Used for converting color maps and such
   background = background.convert()
   # Fill the screen with a black background
   background.fill(black)

   # Create the player paddle object
   player = Player()
   # Create the ball
   ball = Ball()
   # Create a group of 1 ball (used in checking collisions)
   balls = pygame.sprite.Group()
   balls.add(ball)

   # Create a group that will hold the blocks we are about to create
   blocks=pygame.sprite.RenderPlain()
   # The top of the block (y position)
   top = 80
   # Number of blocks to create
   blockcount = 40

   # Create a row of purple blocks
   for i in range(0,blockcount):
       # Create a block (color,x,y,new ball speed,points)
       block=Block(purple,i*20,top,.85,30)
       blocks.add(block)
   top += 15
   #Blue
   for i in range(0,blockcount):
       block=Block(blue,i*20,top,.7,20)
       blocks.add(block)

   top += 15
   # Green
   for i in range(0,blockcount):
       block=Block(green,i*20,top,.55,15)
       blocks.add(block)
   top += 15
   #Yellow
   for i in range(0,blockcount):
       block=Block(([255,255,0]),i*20,top,.4,10)
       blocks.add(block)
   top += 15
   # Red
   for i in range(0,blockcount):
       block=Block(red,i*20,top,.3,5)
       blocks.add(block)


   movingsprites = pygame.sprite.RenderPlain((player,ball))
   clock = pygame.time.Clock()
   block_hit_sound = load_sound('chink.wav')
   block_hit_sound.play()
   done = False
   while 1:
       clock.tick(1000)

       for event in pygame.event.get():
           if event.type == QUIT:
               return

       if not done:
           # Update the player and ball positions
           player.update()
           done = ball.update()

           # If we are done, print game over
           if done:
               text=font.render("Game Over", 1, (200, 200, 200))
               textpos = text.get_rect(centerx=background.get_width()/2)
               textpos.top = 300
               background.blit(text, textpos)
               print "Game Over"

           # See if the ball hits the player paddle
           if pygame.sprite.spritecollide(player, balls, False):
               # The 'diff' lets you try to bounce the ball left or right depending where on the paddle you hit it
               diff = (player.rect.left + player.width/2) - (ball.rect.left+ball.width/2)
               # Set the ball's y position in case we hit the ball on the edge of the paddle
               ball.rect.top = screen.get_height() - player.rect.height - ball.rect.height -1
               ball.bounce(diff)

           # Check for collisions between the ball and the blocks
           deadblocks = pygame.sprite.spritecollide(ball, blocks, False)
           # For every block we hit:
           for b in deadblocks:
               # Speed up the ball if we hit a block that causes ball speed up
               if ball.speed < b.speed:
                   ball.speed = b.speed
               # Add to our score
               score += b.score
               # Remove the block from the list of blocks
               blocks.remove(b)
           # If we actually hit a block, bounce the ball and play a sound
           if len(deadblocks) > 0:
               block_hit_sound.play()
               ball.bounce(0)

           # Print the score
           scoreprint = "Score: "+str(score)
           clearrect = Rect(0,0,250,30)
           pygame.draw.rect(background,black,clearrect)
           text = font.render(scoreprint, 1, white)
           textpos = (0,0)
           background.blit(text, textpos)

           #Draw Everything
           screen.blit(background, (0, 0))
           movingsprites.draw(screen)
           blocks.draw(screen)
           pygame.display.flip()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
