#
# a starting sprite type class
# *lazy loading
# *position, rotation
# * returns a rect that can be used for collision
# 
# a = Agent(art="path/to/image") to create
# a.pos = [150,50] to set position
# a.rot = [-1,0] to set direction vector
# image is drawn by the world, if image not yet loaded it is loaded
# multiple agents with the same image will only load the image once
#
# centered on agent.hotspot, default is [0,0] for upper left corner
# change to modify the hotspot, such as putting it in the center if you want to

import pygame
import math
import random

memory = {}
class Agent(object):
    def __init__(self,art=None,pos=None,rot=None):
        if not pos:
            pos = [0,0]
        if not rot:
            rot = [1,0]
        self.graphics = None
        self.surface = None
        self.pos = pos
        self.rot = rot
        self.art = art
        self.hotspot = [0,0]
        self.rotation_on_rot = False
        self.visible = True
        self.gfd = {}
        self.gft = {}
        self.init()
    def init(self):
        pass
    def load(self,art=None):
        if not art:
            art = self.art
        if not art in memory:
            memory[art] = pygame.image.load(art).convert_alpha()
        self.graphics = memory[art]
        self.surface = self.graphics
        return self
    def update(self,world):
        if self.rotation_on_rot and self.surface:
            ang = math.atan2(-self.rot[1],self.rot[0])*180.0/math.pi
            self.surface = pygame.transform.rotate(self.graphics,ang)
    def draw(self,engine):
        if not self.surface and self.art:
            self.load()
        if self.visible:
            engine.surface.blit(self.surface,[self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1]])
    def rect(self):
        if not self.surface:
            return pygame.Rect([[0,0],[0,0]])
        r = self.surface.get_rect()
        r = r.move(self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1])
        return r