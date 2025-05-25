#!/usr/bin/env python3
import pygame
import sys
import random
from classes import *
from costants import *

def setup_containers():
    containers_scale = Scale(100,100)

    spacing = (WIDTH - (containers_scale.w * 4)) // 5

    containers.clear()
    containers.append(Container(screen,"A",Pos(spacing,600), containers_scale))
    containers.append(Container(screen,"B",Pos(spacing*2 + containers_scale.w,600), containers_scale))
    containers.append(Container(screen,"C",Pos(spacing*3 + (containers_scale.w*2),600), containers_scale))
    containers.append(Container(screen,"D",Pos(spacing*4 + (containers_scale.w*3),600), containers_scale))

def text_to_screen(screen):
    level_text = font.render(f"Level: {actual_level + 1}", True, (0, 0, 0))
    screen.blit(level_text, (1100, 60))

    time_text = font.render(f"Time: {seconds}", True, (0,0,0))
    screen.blit(time_text, (1100,20))

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))

def spawn_trash():
    trash_type = random.choice(["A", "B", "C", "D"])
    pos = Pos(random.randint(0, WIDTH - 50), 0) #Maybe change first zero to 50      
    scale = Scale(*levels[actual_level]["scale"])                             
    velocity = random.randint(*levels[actual_level]["velocity"])                 
    trashes.append(Trash(trash_type, pos, scale, velocity))

def draw_life_bar(screen, current, max_value):
    
    pygame.draw.rect(screen, (180, 180, 180), (20, 60, max_value, 20))  
    pygame.draw.rect(screen, (255, 50, 50), (20, 60, current, 20))      
    pygame.draw.rect(screen, (0, 0, 0), (20, 60, max_value, 20), 2)  




pygame.init()

font = pygame.font.SysFont(None, 36)
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("Game Title")   
clock = pygame.time.Clock()

trashes = []
containers = []

lives = 5
actual_level = 0
score = 0

running = True
dragging = None
mouse_held = None 

level_start_time = pygame.time.get_ticks()
level_finished = False

setup_containers()

max_life_bar = 300
life_bar = max_life_bar

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True

        #if mouse button was released, detects trash-container collision
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False
            if dragging:
                for container in containers:
                    if dragging.rect.colliderect(container.rect):
                        if dragging.trash_type == container.container_type:
                            score += 1
                        else:
                            score -= 1
                            life_bar -= 5
                        if dragging in trashes:
                            trashes.remove(dragging)
                        break
                dragging = None
    
    seconds = (pygame.time.get_ticks() - level_start_time) // 1000
    if seconds >= levels[actual_level]["duration"]:
        level_finished = True

    #Allows grabing trash if mouse is pressed before reaching trash hitbox
    if mouse_held and dragging is None:
        mx, my = pygame.mouse.get_pos()
        for trash in trashes:
            #Gives +10px to trash hitbox
            hit_rect = trash.rect.inflate(10, 10)
            if hit_rect.collidepoint(mx, my):
                dragging = trash
                break

    #If dragging move trash to cursor position
    if dragging:
        mx, my = pygame.mouse.get_pos()
        dragging.rect.center = (mx, my)

    #Background color
    screen.fill((220, 220, 220)) 

    #Draw containers
    for container in containers:
        container.draw(screen)
        
    # Probability of 1/(level[trash_spawn_denominator]) of spawning trash per frame
    if random.randint(1, levels[actual_level]["trash_spawn_denominator"]) == 1:
        spawn_trash()

    for trash in trashes[:]:
        #Don't check collision nor give gravity while dragging trash  
        if trash is dragging:
            continue
        
        trash.gravity()
        #Remove if exceed screen        
        if trash.rect.top > HEIGHT:
            trashes.remove(trash)
            score -= 1
            life_bar -= 2

        #Checks container-trash collision
        for container in containers:
            if trash.rect.colliderect(container.rect):
                if trash.trash_type == container.container_type:
                    score += 1
                else:
                    score -= 1
                    life_bar -= 3
                trashes.remove(trash)
                break

    #Change levels
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
    
    
    #Detects mouse hovers and changes cursor
    mx, my = pygame.mouse.get_pos()
    hovering = any(trash.rect.collidepoint((mx, my)) for trash in trashes)

    if hovering:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    #Draw trash
    for trash in trashes:
        trash.draw(screen)
    
    #Draw text: score,time,level
    text_to_screen(screen)

    #Draw live bar
    draw_life_bar(screen, life_bar, max_life_bar)

    if life_bar <= 0:
        running = False
        print("You Lost!")


    pygame.display.flip()
    clock.tick(FPS)

print(f"Puntaje: {score}")
pygame.quit()
sys.exit()

