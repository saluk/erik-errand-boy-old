#
# world.py
# a simple container of sprites, which are all rendered in order each frame
# subclass for your own scenes to actually do things

import pygame
import random
import time
from agents import *

class World(object):
    def __init__(self,engine):
        self.engine = engine
        self.objects = []
        self.sprites = []
        self.offset = [0,0]    #Offset for rendering
        self.start()
    def add(self,o):
        """Add an object to the scene"""
        self.objects.append(o)
    def start(self):
        """Code that runs when a world starts, base world
        doesn't need to do anything"""
    def update(self):
        """self.sprites starts empty, any object added to the list during
        update() is going to be rendered"""
        self.sprites = []
        for o in self.objects:
            o.update(self)
            if o.visible:
                self.sprites.append(o)
    def draw(self):
        """Iterate sprites and draw them"""
        [s.draw(self.engine,self.offset) for s in self.sprites]
    def input(self,controller):
        """As controller gets functions to check the state of things, input
        can be put here"""

class Text(Agent):
    def set_text(self,text):
        self.surface = None
        self.text = text
        return self
    def render(self,engine):
        if not self.surface:
            self.surface = engine.font.render(self.text,1,[0,255,0])
    def draw(self,engine,offset=[0,0]):
        if not self.surface:
            self.render(engine)
        super(Text,self).draw(engine,offset)

class Player(Agent):
    def init(self):
        self.facing = -1
    def draw(self,engine,offset=[0,0]):
        self.surface = self.graphics
        if self.facing<0:
            self.surface = pygame.transform.flip(self.surface,1,0)
        super(Player,self).draw(engine,offset)
    def left(self):
        self.facing = -1
        self.pos[0]-=2
        if self.map.collide(self):
            self.pos[0]+=2
    def right(self):
        self.facing = 1
        self.pos[0]+=2
        if self.map.collide(self):
            self.pos[0]-=2
    def update(self,dt):
        self.pos[1]+=1
        if self.map.collide(self):
            self.pos[1]-=1

class Tile(Agent):
    def init(self):
        pass
    def is_empty(self):
        return self.index==-1

class Tilemap(Agent):
    def load(self,map):
        self.mapfile = map
        from tiledtmxloader import tmxreader
        self.raw_map = tmxreader.TileMapParser().parse_decode(self.mapfile)

        self.tileset_list = [None]
        for tileset in self.raw_map.tile_sets:
            tileset = pygame.image.load(tileset.images[0].source).convert_alpha()
            x = 0
            y = 0
            while y*32<tileset.get_height():
                self.tileset_list.append(tileset.subsurface([[x*32,y*32],[32,32]]))
                x+=1
                if x*32>=tileset.get_width():
                    x=0
                    y+=1

        self.map = []
        row = []
        for layer in self.raw_map.layers:
            maplayer = []
            x=y=0
            for ti in layer.decoded_content:
                tile = Tile()
                tile.index = ti
                tile.surface = self.tileset_list[tile.index]
                tile.pos = [x*32,y*32]
                row.append(tile)
                x+=1
                if x>=layer.width:
                    x=0
                    y+=1
                    maplayer.append(row)
                    row = []
            self.map.append(maplayer)
    def collide(self,agent):
        top = agent.pos[1]//32
        left = agent.pos[0]//32
        right = (agent.pos[0]+32-1)//32
        bottom = (agent.pos[1]+32-1)//32
        if left<0 or top<0 or right>len(self.map[0]) or bottom>len(self.map):
            return 1
        col = 0
        print left,top,self.map[top][left].index
        points =[(left,top),(right,top),(left,bottom),(right,bottom)]
        for point in points:
            if self.map[point[1]][point[0]].index>0:
                return 1
    def draw(self,engine,offset):
        for layer in self.map:
            for row in layer:
                for tile in row:
                    tile.draw(engine,offset)

class GameWorld(World):
    def start(self):
        self.map = Tilemap()
        self.map.load("dat/castle.tmx")
        
        self.camera = self.offset
        self.scroll_speed = 5

        self.add(self.map)
    def input(self,controller):
        if controller.left:
            self.camera[0]-=self.scroll_speed
        if controller.right:
            self.camera[0]+=self.scroll_speed
        if controller.up:
            self.camera[1]-=self.scroll_speed
        if controller.down:
            self.camera[1]+=self.scroll_speed
    def update(self):
        super(GameWorld,self).update()

def make_world(engine):
    """This makes the starting world"""
    w = GameWorld(engine)
    return w
