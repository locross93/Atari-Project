#!/usr/bin/env python

# ale_python_test1.py
# Author: Ben Goodrich
#
# This is a direct port to python of the shared library example from ALE provided in
# doc/examples/sharedLibraryInterfaceExample.cpp

import sys
from ale_python_interface import ALEInterface
import numpy as np

if(len(sys.argv) > 2):
    print("Usage ./ale_python_test1.py <ROM_FILE_NAME>")
    sys.exit()

ale = ALEInterface()

##max_frames_per_episode = ale.getInt("max_num_frames_per_episode");
##ale.set("random_seed",123)
ale.setInt(b'random_seed', 123)

##random_seed = ale.getInt("random_seed")
random_seed = ale.getInt(b'random_seed')
print("random_seed: " + str(random_seed))

##ale.loadROM(sys.argv[1])
##rom_file = str.encode(sys.argv[1])
##ale.loadROM(rom_file)
ale.loadROM(b"/Users/logancross/Documents/Atari/Arcade-Learning-Environment-master/ale_python_interface/examples/space_invaders.bin")
legal_actions = ale.getLegalActionSet()

for episode in range(10):
    total_reward = 0.0 
    while not ale.game_over():
        a = legal_actions[np.random.randint(legal_actions.size)]
        ##a = legal_actions[randrange(len(legal_actions))]
        reward = ale.act(a);
        total_reward += reward
    print("Episode " + str(episode) + " ended with score: " + str(total_reward))
    ale.reset_game()

