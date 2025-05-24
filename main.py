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
font = pygame.font.SysFont(None, 36)

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

lives = 5

actual_level = 0

levels = [
    {"duration": 30, "velocity": (3,6), "extra_lives": 5,"scale":(80,80), "trash_spawn_denominator": 50},
    {"duration": 35, "velocity": (3,6), "extra_lives": 4,"scale":(70,70), "trash_spawn_denominator": 40},
    {"duration": 40, "velocity": (4,7), "extra_lives": 3,"scale":(60,60), "trash_spawn_denominator": 30},
]
level_start_time = pygame.time.get_ticks()
level_finished = False
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
    
    seconds = (pygame.time.get_ticks() - level_start_time) // 1000
    if seconds >= levels[actual_level]["duration"]:
        level_finished = True

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
        

    if random.randint(1, levels[actual_level]["trash_spawn_denominator"]) == 1:
        trash_type = random.choice(["A", "B", "C", "D"])
        pos = Pos(random.randint(0, WIDTH - 50), 0)      
        scale = Scale(*levels[actual_level]["scale"])                             
        velocity = random.randint(*levels[actual_level]["velocity"])                 
        trashes.append(Trash(trash_type, pos, scale, velocity))

    for trash in trashes[:]: 
        if trash is dragging:
            continue

        trash.gravity()        
        if trash.rect.top > HEIGHT:
            trashes.remove(trash)
            score -= 1

        for container in containers:
            if trash.rect.colliderect(container.rect):
                if trash.trash_type == container.container_type:
                    score += 1
                else:
                    score -= 1
                trashes.remove(trash)
                break

    if level_finished:
        actual_level += 1
        if actual_level >= len(levels):
            print("\nGame Completed")
            running = False
        else:
            level_start_time = pygame.time.get_ticks()
            level_finished = False
            lives += levels[actual_level]["extra_lives"]
            trashes.clear()  
            dragging = None

    level_text = font.render(f"Level: {actual_level + 1}", True, (0, 0, 0))
    screen.blit(level_text, (20, 100))

    time_text = font.render(f"Time: {seconds}", True, (0,0,0))
    screen.blit(time_text, (1100,20))
    
    mx, my = pygame.mouse.get_pos()

   
    hovering = any(trash.rect.collidepoint((mx, my)) for trash in trashes)

    if hovering:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    for trash in trashes:
        trash.draw(screen)
        
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

print(f"Puntaje: {score}")
pygame.quit()
sys.exit()

