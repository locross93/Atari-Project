import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((200,200))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            print("it worked")
        elif event.type == pygame.KEYUP and event.key == pygame.K_d:
            print("It didn't work")


    #compute how many milliseconds have passed since the previous call
    clock.tick(30)
        
