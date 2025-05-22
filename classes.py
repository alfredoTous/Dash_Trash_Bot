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
            color = (255, 0, 0)
        elif self.trash_type == "B":
            color = (0, 255, 0)
        elif self.trash_type == "C":
            color = (0, 0, 255)
        elif self.trash_type == "D":
            color = (150, 150, 150)

        pygame.draw.rect(screen, color, self.rect)


class Container:

    def __init__(self,screen,container_type,pos,scale):
        self.container_type = container_type
        self.rect = pygame.Rect(pos.x, pos.y, scale.w, scale.h)
        
    def draw(self, screen):
        if self.container_type == "A":
            color = (255, 0, 0)
        elif self.container_type == "B":
            color = (0, 255, 0)
        elif self.container_type == "C":
            color = (0, 0, 255)
        elif self.container_type == "D":
            color = (150, 150, 150)
        pygame.draw.rect(screen, color, self.rect)

class Pos:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Scale:
    def __init__(self,w,h):
        self.w = w
        self.h = h 

        


    