#!/usr/bin/env python3
import pygame
import sys
import random
from classes import *

def setup_containers():
    containers_scale = Scale(100,100)

    spacing = (WIDTH - (containers_scale.w * 4)) // 5

    containers.clear()
    containers.append(Container(screen,"A",Pos(spacing,600), containers_scale))
    containers.append(Container(screen,"B",Pos(spacing*2 + containers_scale.w,600), containers_scale))
    containers.append(Container(screen,"C",Pos(spacing*3 + (containers_scale.w*2),600), containers_scale))
    containers.append(Container(screen,"D",Pos(spacing*4 + (containers_scale.w*3),600), containers_scale))
    

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Game Title")   

clock = pygame.time.Clock()
FPS = 60

trashes = []
containers = []

running = True
setup_containers()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((220, 220, 220)) 

    for container in containers:
        container.draw(screen)

    if random.randint(1, 30) == 1:
        trash_type = random.choice(["A", "B", "C", "D"])
        pos = Pos(random.randint(0, WIDTH - 50), 0)      
        scale = Scale(50, 50)                            
        velocity = random.randint(3, 7)                 
        trashes.append(Trash(trash_type, pos, scale, velocity))

    for trash in trashes[:]: 
        trash.gravity()        
        if trash.rect.top > HEIGHT:
            trashes.remove(trash)

    
    for trash in trashes:
        trash.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

