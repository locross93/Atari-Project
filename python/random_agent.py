import sys
from random import randrange
from ale_python_interface import ALEInterface

if len(sys.argv) < 2:
  print("Usage:", sys.argv[0], "rom_file")
  sys.exit()

ale = ALEInterface()
##ale.setInt('random_seed', 123)
ale.loadROM(sys.argv[1])

# Get the list of legal actions
legal_actions = ale.getLegalActionSet()
total_reward = 0

while not ale.game_over():
  a = legal_actions[randrange(len(legal_actions))]
  reward = ale.act(1);
  total_reward += reward
print("Episode ended with score:", total_reward)