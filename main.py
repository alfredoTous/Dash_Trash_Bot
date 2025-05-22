#!/usr/bin/env python3
import pygame
import sys
import random
from classes import *

def setup_containers():
    containers_scale = Scale(100,100)

    spacing = (WIDTH - (containers_scale.w * 4)) // 5

    container_1 = Container(screen,"A",Pos(spacing,600), containers_scale)
    container_2 = Container(screen,"B",Pos(spacing*2 + containers_scale.w,600), containers_scale)
    container_3 = Container(screen,"C",Pos(spacing*3 + (containers_scale.w*2),600), containers_scale)
    container_4 = Container(screen,"D",Pos(spacing*4 + (containers_scale.w*3),600), containers_scale)

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

    
    setup_containers()


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

