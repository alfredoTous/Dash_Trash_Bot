#!/usr/bin/env python3 
import pygame 

class Trash:

    def __init__(self,screen,trash_type):
        self.trash_type = trash_type


class Container:

    def __init__(self,screen,container_type,pos):
        self.container_type = container_type
        
        if container_type == "A":
            rect = pygame.draw.rect(screen, (255,0,0), pygame.Rect(pos.x,pos.y,60,60))
        elif container_type == "B":
            rect = pygame.draw.rect(screen, (0,255,0), pygame.Rect(pos.x,pos.y,60,60))
        elif container_type == "C":
            rect = pygame.draw.rect(screen, (0,0,255), pygame.Rect(pos.x,pos.y,60,60))
        elif container_type == "D":
            rect = pygame.draw.rect(screen, (150,150,150), pygame.Rect(pos.x,pos.y,60,60))

class Pos:
    def __init__(self,x,y):
        self.x = x
        self.y = y

        


    