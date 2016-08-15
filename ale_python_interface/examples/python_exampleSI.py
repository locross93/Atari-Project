#!/usr/bin/env python
# python_example.py
# Author: Ben Goodrich
#
# This is a direct port to python of the shared library example from
# ALE provided in doc/examples/sharedLibraryInterfaceExample.cpp
import sys
from random import randrange
import numpy as np
from ale_python_interface import ALEInterface

if len(sys.argv) > 2:
  print('Usage: %s rom_file' % sys.argv[0])
  sys.exit()

ale = ALEInterface()

# Get & Set the desired settings
ale.setInt(b'random_seed', 123)

# Set USE_SDL to true to display the screen. ALE must be compilied
# with SDL enabled for this to work. On OSX, pygame init is used to
# proxy-call SDL_main.
USE_SDL = True
if USE_SDL:
  if sys.platform == 'darwin':
    import pygame
    pygame.init()
    ale.setBool(b'sound', False) # Sound doesn't work on OSX
  elif sys.platform.startswith('linux'):
    ale.setBool(b'sound', True)
  ale.setBool(b'display_screen', True)

# Load the ROM file
##rom_file = str.encode(sys.argv[1])
##ale.loadROM(rom_file)
ale.loadROM(b"/Users/logancross/Documents/Atari/Arcade-Learning-Environment-master/ale_python_interface/examples/space_invaders.bin")

# Get the list of legal actions
legal_actions = ale.getLegalActionSet()

# Play 10 episodes
for episode in range(10):
  total_reward = 0
  total_action = 0
  while not ale.game_over():
    a = legal_actions[randrange(len(legal_actions))]
    # Apply an action and get the resulting reward
    (reward,action) = ale.act(a);
    total_reward += reward
    total_action += action
    #get RAM
    ram_size = ale.getRAMSize()
    ram = np.zeros((ram_size),dtype=np.uint8)
    ale.getRAM(ram)
    print(ram)
  print('Episode %d ended with score: %d' % (episode, total_reward))
  ale.reset_game()
