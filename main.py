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

dragging = None
score = 0
mouse_held = None 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False
            if dragging:
                for container in containers:
                    if dragging.rect.colliderect(container.rect):
                        if dragging.trash_type == container.container_type:
                            score += 1
                        else:
                            score -= 1
                        if dragging in trashes:
                            trashes.remove(dragging)
                        break
                dragging = None

    if mouse_held and dragging is None:
        mx, my = pygame.mouse.get_pos()
        for trash in trashes:
            hit_rect = trash.rect.inflate(10, 10)
            if hit_rect.collidepoint(mx, my):
                dragging = trash
                break

    if dragging:
        mx, my = pygame.mouse.get_pos()
        dragging.rect.center = (mx, my)

    screen.fill((220, 220, 220)) 

    for container in containers:
        container.draw(screen)
        

    if random.randint(1, 50) == 1:
        trash_type = random.choice(["A", "B", "C", "D"])
        pos = Pos(random.randint(0, WIDTH - 50), 0)      
        scale = Scale(70, 70)                            
        velocity = random.randint(3, 7)                 
        trashes.append(Trash(trash_type, pos, scale, velocity))

    for trash in trashes[:]: 
        trash.gravity()        
        if trash.rect.top > HEIGHT:
            trashes.remove(trash)

        for container in containers:
            if trash.rect.colliderect(container.rect):
                if trash.trash_type == container.container_type:
                    score += 1
                else:
                    score -= 1
                trashes.remove(trash)
                break
    mx, my = pygame.mouse.get_pos()

   
    hovering = any(trash.rect.collidepoint((mx, my)) for trash in trashes)

    if hovering:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    for trash in trashes:
        trash.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

print(f"Puntaje: {score}")
pygame.quit()
sys.exit()

