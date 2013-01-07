#
# world.py
# a simple container of sprites, which are all rendered in order each frame
# subclass for your own scenes to actually do things

import pygame
import random
import os
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
        o.world = self
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
                self.sprites.extend(o.get_sprites())
        self.sprites.sort(key=lambda sprite:(sprite.layer,sprite.pos[1]))
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
        self.hotspot = [16,32]
        self.facing = [-1,0]
        self.next_frame = 10
        self.animdelay = 5
        self.frame = 0
        self.anim = None
        self.animating = False
        self.walk_speed = 2
        self.vector = [0,0]
    def load(self,spritesheet):
        super(Player,self).load(spritesheet)
        self.anims = {}
        order = ["down","left","right","up"]
        for y in range(4):
            frames = []
            for x in range(4):
                frames.append(self.graphics.subsurface([[x*32,y*48],[32,48]]))
            self.anims[order[y]] = frames
    def draw(self,engine,offset=[0,0]):
        super(Player,self).draw(engine,offset)
    def idle(self):
        self.animating = False
        self.vector = [0,0]
    def walk(self):
        bounce = 0
        if self.vector[0]:
            bounce += 1
            self.pos[0]+=self.vector[0]*self.walk_speed
            if self.map.collide(self):
                self.pos[0]-=self.vector[0]*self.walk_speed
                bounce -= 1
            else:
                self.facing = [self.vector[0],0]
        if self.vector[1]:
            bounce += 1
            self.pos[1]+=self.vector[1]*self.walk_speed
            if self.map.collide(self):
                self.pos[1]-=self.vector[1]*self.walk_speed
                bounce -= 1
            else:
                self.facing = [0,self.vector[1]]
        if bounce:
            self.animating = True
    def left(self):
        self.facing = [-1,0]
        self.vector[0] = -1
    def right(self):
        self.facing = [1,0]
        self.vector[0] = 1
    def up(self):
        self.facing = [0,-1]
        self.vector[1] = -1
    def down(self):
        self.facing = [0,1]
        self.vector[1] = 1
    def set_anim(self,anim):
        self.anim = anim
        self.frame = 0
        self.next_frame = self.animdelay
        self.set_animation_frame()
    def set_animation_frame(self):
        anim = self.anims[self.anim]
        if self.frame>=len(anim):
            self.frame = 0
        self.surface = anim[self.frame]
    def update(self,dt):
        if self.facing[0]<0:
            anim = "left"
        elif self.facing[0]>0:
            anim = "right"
        elif self.facing[1]<0:
            anim = "up"
        elif self.facing[1]>0:
            anim = "down"
        else:
            anim = self.anim
        if anim!=self.anim:
            self.set_anim(anim)
        if self.animating:
            self.next_frame -= 1
        if self.next_frame<=0:
            self.next_frame = self.animdelay
            self.frame += 1
            self.set_animation_frame()
            
        if self.vector[0] or self.vector[1]:
            self.walk()

class Tile(Agent):
    def init(self):
        pass
    def is_empty(self):
        return self.index==-1
        
class TileLayer(Agent):
    def init(self):
        self.tiles = []
    def draw(self,engine,offset):
        for row in self.tiles:
            for tile in row:
                tile.draw(engine,offset)

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
        for i,layer in enumerate(self.raw_map.layers):
            maplayer = TileLayer()
            maplayer.layer = i
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
                    maplayer.tiles.append(row)
                    row = []
            self.map.append(maplayer)
            self.map_width = len(maplayer.tiles[0])
            self.map_height = len(maplayer.tiles)
        self.collisions = self.map[-1].tiles
        del self.map[-1]
    def collide(self,agent):
        top = (agent.pos[1]-16)//32
        left = (agent.pos[0]-16)//32
        right = (agent.pos[0]+16-1)//32
        bottom = (agent.pos[1]+16-1)//32
        if left<0 or top<0 or right>self.map_width or bottom>self.map_height:
            return 1
        col = 0
        points =[(left,top),(right,top),(left,bottom),(right,bottom)]
        for point in points:
            if self.collisions[point[1]][point[0]].index>0:
                return 1
    def get_sprites(self):
        return [layer for layer in self.map]

class GameWorld(World):
    def start(self):
        self.map = Tilemap()
        self.map.load("dat/castle.tmx")
        
        self.camera = self.offset
        
        self.scroll_speed = 5

        self.add(self.map)

        for i in range(5):
            self.player = Player()
            art = [x for x in os.listdir("art/sprites") if x.endswith(".png")]
            f = random.choice(art)
            self.player.load("art/sprites/"+f)
            self.player.pos = [random.randint(0,39*32),random.randint(0,29*32)]
            random.choice([self.player.up,self.player.down,self.player.left,self.player.right])()
            self.player.idle()
            self.player.map = self.map
            self.add(self.player)
        
        self.camera_focus = self.player
    def input(self,controller):
        self.player.idle()
        if controller.left:
            self.player.left()
        if controller.right:
            self.player.right()
        if controller.up:
            self.player.up()
        if controller.down:
            self.player.down()
    def update(self):
        super(GameWorld,self).update()
        self.focus_camera()
        
    def focus_camera(self):
        if not self.camera_focus:
            return
        self.camera[:] = [self.camera_focus.pos[0]-5*32,self.camera_focus.pos[1]-4*32]
        if self.camera[0]<0:
            self.camera[0] = 0
        if self.camera[1]<0:
            self.camera[1] = 0

def make_world(engine):
    """This makes the starting world"""
    w = GameWorld(engine)
    return w
