import pygame
import random

from agents import Agent
from items import Item
from ui import Textbox

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
        
        self.radius = 14   #collision radius around hotspot
        
        self.last_hit = None
        
        self.following = None
        self.following_points = []
        
        self.last_random_point = None
        self.next_random_point = 0
        
        self.items = []
        names = Item.names[:]
        for i in range(random.randint(1,4)):
            name = random.choice(names)
            names.remove(name)
            item = Item()
            item.name = name
            self.items.append(item)
        
        self.menu = None
        self.texter = None
        
        self.pickpocketing = None
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
        elipserect = [[0,0],[20,12]]
        elipse = pygame.Surface([20,12]).convert_alpha()
        elipse.fill([0,0,0,0])
        pygame.draw.ellipse(elipse,[0,0,0,150],elipserect)
        engine.surface.blit(elipse,[self.pos[0]-offset[0]-10,self.pos[1]-offset[1]-6+12])
        super(Player,self).draw(engine,offset)
        x,y = (self.pos[0])//32*32-offset[0],(self.pos[1])//32*32-offset[1]
        w,h = 32,32
        #pygame.draw.rect(engine.surface,[255,0,255],pygame.Rect([[x,y],[w,h]]))
        for p in self.following_points:
            pygame.draw.rect(engine.surface,[255,0,255],[[p[0]-offset[0],p[1]-offset[1]],[2,2]])
    def idle(self):
        self.animating = False
        self.vector = [0,0]
    def walk(self):
        moved = False
        col1=col2=None
        
        #calculate inside collisions
        col0 = self.world.collide(self)
        
        if self.vector[0]:
            self.pos[0]+=self.vector[0]*self.walk_speed
            col1 = self.world.collide(self,"move")
            if col1 and not col0:
                self.pos[0]-=self.vector[0]*self.walk_speed
            else:
                self.facing = [self.vector[0],0]
                moved = True
        if self.vector[1]:
            self.pos[1]+=self.vector[1]*self.walk_speed
            col2 = self.world.collide(self,"move")
            if col2 and not col0:
                self.pos[1]-=self.vector[1]*self.walk_speed
            else:
                self.facing = [0,self.vector[1]]
                moved = True
        
        hit_any = None
        for col in col1,col2:
            if col:
                hit_any = col
                if isinstance(col,dict):
                    if "warptarget" in col:
                        self.world.change_map(self,col["map"],col["warptarget"])
                        
        if hit_any:
            self.last_hit = hit_any
        else:
            self.last_hit = None
        
        if moved:
            self.animating = True
    def say(self,text):
        self.texter = Textbox()
        self.texter.to_say = text
        self.world.add(self.texter)
        print self.texter,self.texter.to_say,self.texter.said,self.texter.pos
    def frobme(self,actor):
        if actor.menu:
            options = []
            if self.following==actor:
                options.append( ("'Stop'",self.action_unfollow,(actor,None)) )
            else:
                options.append( ("'follow me!'",self.action_follow,(actor,None)) )
                options.append( ("pickpocket",self.action_pickpocket,(actor,None)) )
                options.append( ("slip in pocket",self.action_putpocket,(actor,None)) )
            actor.menu.setup(options)
    def mymenu(self):
        if not self.menu:
            return
        options = []
        if self.items:
            options.append( ("items",self.show_items,(self,None)) )
        else:
            options.append( ("no items",self.show_items,(self,None)) )
        self.menu.setup(options)
    def show_items(self,actor,item):
        if not self.menu:
            returrn
        options = []
        for i in self.items:
            options.append( (i.name,self.examine_item,(self,i)) )
        self.menu.setup(options)
    def examine_item(self,actor,item):
        self.say("The item is named "+item.name)
    def action_follow(self,actor,item):
        self.following = actor
    def action_unfollow(self,actor,item):
        self.following = None
        self.following_points = []
    def action_pickpocket(self,actor,item):
        if actor.menu:
            options = []
            for i in self.items:
                options.append( (i.name,self.action_pickitem,(actor,i)) )
            actor.menu.setup(options,pause=False)
        self.pickpocketing = actor
    def action_putpocket(self,actor,item):
        if actor.menu:
            options = []
            for i in actor.items:
                options.append( (i.name,self.action_putitem,(actor,i)) )
            actor.menu.setup(options)
    def action_pickitem(self,actor,item):
        actor.items.append(item)
        self.items.remove(item)
    def action_putitem(self,actor,item):
        self.items.append(item)
        actor.items.remove(item)
    def action(self):
        """Interact with object in front of us"""
        p = self.pos[:]
        for s in range(3):
            p[0]+=self.facing[0]*8
            p[1]+=self.facing[1]*8
            col = self.world.collide_point(self,p,"frobme")
            if col:
                print col,dir(col)
                if hasattr(col,"frobme"):
                    col.frobme(self)
                return
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
        if self.vector[0] or self.vector[1]:
            self.walk()
            
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
            
        if self.pickpocketing:
            t = self.pickpocketing
            #Check if we can see the target
            #Check if the distance is too great
            if self.distance(t)>18:
                t.menu.disable()
                self.pickpocketing = None
    def collide(self,agent,flags=None):
        return self.collide_point(agent.pos,flags)
    def collide_point(self,p,flags=None):
        radius = self.radius
        left,top,right,bottom = self.pos[0]-radius+1,self.pos[1]-radius+1,self.pos[0]+radius-1,self.pos[1]+radius-1
        if p[0]>=left and p[0]<=right and p[1]>=top and p[1]<=bottom:
            return self
    def rect(self):
        radius = self.radius
        left,top,right,bottom = self.pos[0]-radius+1,self.pos[1]-radius+1,self.pos[0]+radius-1,self.pos[1]+radius-1
        return pygame.Rect([[left,top],[right-left,bottom-top]])
