import os,random

from world import World
from tiles import TileMap
from characters import Player

class GameWorld(World):
    def start(self):
        self.map = TileMap()
        self.maps = {}
        for map in "castle","room1":
            self.maps[map] = TileMap()
            self.maps[map].load("dat/%s.tmx"%map)
        self.map = self.maps["room1"]
        
        self.camera = self.offset
        
        self.scroll_speed = 5

        self.add(self.map)

        for i in range(5):
            self.player = Player()
            art = [x for x in os.listdir("art/sprites") if x.endswith(".png")]
            f = random.choice(art)
            self.player.load("art/sprites/"+f)
            spawn = self.map.regions["spawn"]
            self.player.pos = [random.randint(spawn.left,spawn.right),random.randint(spawn.top,spawn.bottom)]
            random.choice([self.player.up,self.player.down,self.player.left,self.player.right])()
            self.player.idle()
            self.add(self.player)
        self.player.load("art/sprites/erik.png")
        
        self.camera_focus = self.player
    def collide(self,agent):
        for ob in self.objects:
            if ob==agent:
                continue
            if ob.collide(agent):
                return 1
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