import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((200,200))

clock = pygame.time.Clock()

while True:
    pygame.event.pump()
    keypressed = pygame.key.get_pressed()

    if keypressed[pygame.K_UP]:
        print("it worked")
    else: 
        print("It didn't work")

    #compute how many milliseconds have passed since the previous call
    clock.tick(30)
        
