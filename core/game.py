import os,random

from world import World
from tiles import TileMap
from characters import Player

class GameWorld(World):
    def start(self):
        self.maps = {}
        for map in "castle","room1":
            self.maps[map] = TileMap()
            self.maps[map].load("dat/%s.tmx"%map)
        
        self.camera = self.offset
        
        self.scroll_speed = 5
        
        for mapkey in self.maps:
            if "playerspawn" in self.maps[mapkey].regions:
                spawn = self.maps[mapkey].regions["playerspawn"]
                self.player = self.add_character(map=mapkey,sprite="art/sprites/erik.png",pos=[spawn.x+16,spawn.y+16],direction="down")
                self.map = self.maps[mapkey]
            for i in range(5):
                spawn = self.maps[mapkey].regions["spawn"]
                pos = [random.randint(spawn.left,spawn.right),random.randint(spawn.top,spawn.bottom)]
                direction = random.choice(["up","down","left","right"])
                art = [x for x in os.listdir("art/sprites") if x.endswith(".png")]
                sprite = "art/sprites/"+random.choice(art)
                self.add_character(map=mapkey,sprite=sprite,pos=pos,direction=direction)
        
        self.add(self.map)
        self.camera_focus = self.player
    def add_character(self,map,sprite,pos,direction):
        p = Player()
        p.map = map
        p.pos = pos
        p.load(sprite)
        getattr(p,direction)()
        p.idle()
        self.add(p)
        return p
    def change_map(self,character,map,target):
        character.map = map
        target = self.maps[map].destinations[target]
        character.pos = [target.left,target.top]
        if character == self.player:
            self.remove(self.map)
            self.map = self.maps[map]
            self.add(self.map)
    def collide(self,agent):
        for ob in self.objects:
            if ob==agent:
                continue
            col = ob.collide(agent)
            if col:
                return col
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