import os,random

from world import World
from tiles import TileMap
from characters import Player
from aicontroller import AIController

from ui import Radial
from agents import Text

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
        
        self.camera_focus = self.player
        
        self.player.menu = Radial()
        self.player.menu.layer = 10
        self.player.menu.pos = self.player.pos
        self.add(self.player.menu)
        
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
        print "change map",character,map,target
        character.map = map
        target = self.maps[map].destinations[target]
        character.pos = [target.left,target.top]
    def get_objects(self,agent):
        return [self.maps[agent.map]] + [o for o in self.objects if (not hasattr(o,"map") or o.map==agent.map)]
    def update(self):
        """self.sprites starts empty, any object added to the list during
        update() is going to be rendered"""
        self.sprites = []
        self.ai()
        for m in self.maps.values():
            m.update(self)
        for o in self.objects:
            o.update(self)
        for o in self.get_objects(self.camera_focus):
            if o.visible:
                self.sprites.extend(o.get_sprites())
        self.sprites.sort(key=lambda sprite:(sprite.layer,sprite.pos[1]))
        
        self.focus_camera()
        self.player.menu.pos = self.player.pos
    def collide(self,agent):
        for ob in self.get_objects(agent):
            if ob==agent:
                continue
            col = ob.collide(agent)
            if col:
                return col
    def collide_point(self,agent,p):
        for ob in self.get_objects(agent):
            if ob==agent:
                continue
            col = ob.collide_point(p)
            if col:
                return col
    def input(self,controller):
        self.player.idle()
        if controller.menu:
            self.player.menu.visible = not self.player.menu.visible
        if self.player.menu.visible:
            if controller.left:
                controller.left = False
                self.player.menu.rotate_left()
            if controller.right:
                controller.right = False
                self.player.menu.rotate_right()
            if controller.action:
                self.player.menu.action()
        else:
            if controller.left:
                self.player.left()
            if controller.right:
                self.player.right()
            if controller.up:
                self.player.up()
            if controller.down:
                self.player.down()
            if controller.action:
                self.player.action()
    def ai(self):
        for ob in self.objects:
            if isinstance(ob,Player) and not ob==self.player:
                if not hasattr(ob,"aicontroller"):
                    ob.aicontroller = AIController(ob)
                ob.aicontroller.control()
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