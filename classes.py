#!/usr/bin/env python3 
import pygame

class Trash:

    def __init__(self, trash_type, pos, scale, velocity):
        self.trash_type = trash_type
        self.velocity = velocity  
        self.rect = pygame.Rect(pos.x, pos.y, scale.w, scale.h)

    def gravity(self):
        self.rect.y += self.velocity

    def draw(self, screen):
        if self.trash_type == "A":
            color = (194, 126, 0)
        elif self.trash_type == "B":
            color = (194, 0, 0)
        elif self.trash_type == "C":
            color = (0, 0, 194)
        elif self.trash_type == "D":
            color = (0, 194, 0)
            

        pygame.draw.rect(screen, color, self.rect)


class Container:
    CONTAINER_WIDTH = 64
    CONTAINER_HEIGHT = 64

    CONTAINER_SPRITE_MAP = {
        "A": pygame.Rect(0, 0, CONTAINER_WIDTH, CONTAINER_HEIGHT),
        "B": pygame.Rect(64, 0, CONTAINER_WIDTH, CONTAINER_HEIGHT),
        "C": pygame.Rect(128, 0, CONTAINER_WIDTH, CONTAINER_HEIGHT),
        "D": pygame.Rect(192, 0, CONTAINER_WIDTH, CONTAINER_HEIGHT)
    }

    SPRITESHEET = None
    
    def __init__(self,screen,container_type,pos,scale):
        
        self.container_type = container_type

        self.rect = pygame.Rect(pos.x, pos.y, scale.w, scale.h)
        self.image = pygame.transform.scale(
            Container.SPRITESHEET.subsurface(Container.CONTAINER_SPRITE_MAP[container_type]),
            (scale.w, scale.h)
        )
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)  # Borde verde

    def load_container_sprite():
        Container.SPRITESHEET = pygame.image.load("./assets/containers.png").convert_alpha()
        

class Pos:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Scale:
    def __init__(self,w,h):
        self.w = w
        self.h = h 

        


    