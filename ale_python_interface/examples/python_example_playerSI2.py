#!/usr/bin/env python
# python_example.py
# Author: Ben Goodrich
#
# This is a direct port to python of the shared library example from
# ALE provided in doc/examples/sharedLibraryInterfaceExample.cpp
import sys
from random import randrange
from ale_python_interface import ALEInterface
import numpy as np
import pygame
from pygame.locals import *

key_action_tform_table = (
0, #00000 none
2, #00001 up
5, #00010 down
2, #00011 up/down (invalid)
4, #00100 left
7, #00101 up/left
9, #00110 down/left
7, #00111 up/down/left (invalid)
3, #01000 right
6, #01001 up/right
8, #01010 down/right
6, #01011 up/down/right (invalid)
3, #01100 left/right (invalid)
6, #01101 left/right/up (invalid)
8, #01110 left/right/down (invalid)
6, #01111 up/down/left/right (invalid)
1, #10000 fire
10, #10001 fire up
13, #10010 fire down
10, #10011 fire up/down (invalid)
12, #10100 fire left
15, #10101 fire up/left
17, #10110 fire down/left
15, #10111 fire up/down/left (invalid)
11, #11000 fire right
14, #11001 fire up/right
16, #11010 fire down/right
14, #11011 fire up/down/right (invalid)
11, #11100 fire left/right (invalid)
14, #11101 fire left/right/up (invalid)
16, #11110 fire left/right/down (invalid)
14  #11111 fire up/down/left/right (invalid)
)

if len(sys.argv) > 2:
  print('Usage: %s rom_file' % sys.argv[0])
  sys.exit()

ale = ALEInterface()

# Get & Set the desired settings
max_frames_per_episode = ale.getInt(b"max_num_frames_per_episode");
ale.setInt(b'random_seed', 123)

# Set USE_SDL to true to display the screen. ALE must be compilied
# with SDL enabled for this to work. On OSX, pygame init is used to
# proxy-call SDL_main.
USE_SDL = True
if USE_SDL:
  if sys.platform == 'darwin':
    pygame.init()
    ale.setBool(b'sound', False) # Sound doesn't work on OSX
  elif sys.platform.startswith('linux'):
    ale.setBool(b'sound', True)
  ale.setBool(b'display_screen', True)

# Load the ROM file
##rom_file = str.encode(sys.argv[1])
ale.loadROM(b"/Users/logancross/Documents/Atari/Arcade-Learning-Environment-master/ale_python_interface/examples/space_invaders.bin")

(screen_width,screen_height) = ale.getScreenDims()
print("width/height: " +str(screen_width) + "/" + str(screen_height))

(display_width,display_height) = (512,420)

#init pygame
pygame.init()
screen = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Arcade Learning Environment Random Agent Display")

game_surface = pygame.Surface((screen_width,screen_height))

pygame.display.flip()

clock = pygame.time.Clock()

# Get the list of legal actions
legal_actions = ale.getLegalActionSet()

# Play 10 episodes
for episode in range(10):
  total_reward = 0
  while not ale.game_over():
    a = 0;
    for event in pygame.event.get():
      
      if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        a = 2;
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        a = 5;
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
        a = 4;
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        a = 3;
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
        a = 1;
        
    reward = ale.act(a);
    total_reward += reward

    #clear screen
    screen.fill((0,0,0))
    
    #get atari screen pixels and blit them
    numpy_surface = np.frombuffer(game_surface.get_buffer(),dtype=np.int32)
    ##numpy_surface = np.zeros(screen_width*screen_height,dtype=np.uint32)
    ale.getScreenRGB(numpy_surface)
    del numpy_surface
    screen.blit(pygame.transform.scale(game_surface,(display_width,display_height)),(0,0))

    pygame.display.flip()


    #delay to 60fps
    clock.tick(60.)
    
  print('Episode %d ended with score: %d' % (episode, total_reward))
  ale.reset_game()
