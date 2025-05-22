#!/usr/bin/env python3
import pygame
import sys
import random
from classes import *

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Game Title")   

clock = pygame.time.Clock()
FPS = 60

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((220, 220, 220)) 

    # Aquí irá todo lo que se dibuje (basura, contenedores, puntaje...)

    trash_type = random.randint(1,4)

    container_1 = Container(screen,"A",Pos(100,0))



    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
