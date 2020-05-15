import sys
import pygame
import os

pygame.joystick.init()
pygame.init()
import time

print('Found {} joysticks'.format(pygame.joystick.get_count()))

print('now entering loop')
while True:
    event_list = pygame.event.get()
    #os.system('cls' if os.name == 'nt' else 'clear')
    print(event_list)
    time.sleep(0.25)

