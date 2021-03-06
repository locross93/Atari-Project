#!/usr/bin/env python

# ale_python_test_pygame_player.py
# Author: Ben Goodrich
#
# This modified ale_python_test_pygame.py to provide a fully interactive experience allowing the player
# to play. RAM Contents, current action, and reward are also displayed.
# keys are:
# arrow keys -> up/down/left/right
# z -> fire button
import sys
from ale_python_interface import ALEInterface
import numpy as np
import pygame


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

if(len(sys.argv) > 2):
    print("Usage ./ale_python_test_pygame_player.py <ROM_FILE_NAME>")
    sys.exit()
    
ale = ALEInterface()

max_frames_per_episode = ale.getInt(b"max_num_frames_per_episode");
##ale.set("random_seed",123)

# Get & Set the desired settings
ale.setInt(b'random_seed', 123)
ale.setInt(b'frame_skip', 1)

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

random_seed = ale.getInt(b"random_seed")
print("random_seed: " + str(random_seed))

##rom_file = str.encode(sys.argv[1])
##ale.loadROM(rom_file)
##print(rom_file)
ale.loadROM(b"/Users/logancross/Documents/Atari/Arcade-Learning-Environment-master/ale_python_interface/examples/space_invaders.bin")
legal_actions = ale.getMinimalActionSet()
print(legal_actions)

(screen_width,screen_height) = ale.getScreenDims()
print("width/height: " +str(screen_width) + "/" + str(screen_height))

(display_width,display_height) = (1024,420)

#init pygame
pygame.init()
screen = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Arcade Learning Environment Player Agent Display")
##pygame.key.set_repeat(1,5)

game_surface = pygame.Surface((screen_width,screen_height))

pygame.display.flip()

#init clock
clock = pygame.time.Clock()

episode = 0
total_reward = 0.0
a = 0;
while(episode < 10):

    #get the keys

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
 
        elif event.type == pygame.KEYDOWN:
            print(event)
            if event.key == pygame.K_LEFT:
                a = 4;
            elif event.key == pygame.K_RIGHT:
                a = 3;
            elif event.key == pygame.K_UP:
                a = 2;
            elif event.key == pygame.K_DOWN:
                a = 5;
 
        elif event.type == pygame.KEYUP:
            print(event)
            a = 0;
    
    
    reward = ale.act(a);
    total_reward += reward
    #clear screen
    screen.fill((0,0,0))

    pygame.display.flip()


    #delay to 60fps
    clock.tick(60.)

    if(ale.game_over()):
        episode_frame_number = ale.getEpisodeFrameNumber()
        frame_number = ale.getFrameNumber()
        print("Frame Number: " + str(frame_number) + " Episode Frame Number: " + str(episode_frame_number))
        print("Episode " + str(episode) + " ended with score: " + str(total_reward))
        ale.reset_game()
        total_reward = 0.0 
        episode = episode + 1

