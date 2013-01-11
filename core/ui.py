import math

import pygame

from agents import Agent,Text

class Radial(Agent):
    def init(self):
        self.options = []
        self.radius = 0
        self.target_radius = 48
        self.pause = False
        
        self.overlay = pygame.Surface([320,240])
        self.overlay.fill([0,0,0])
        self.overlay.set_alpha(50)
    def update(self,world):
        if self.radius<self.target_radius:
            self.radius += 4
    def draw(self,engine,offset=[0,0]):
        if not self.options:
            self.visible = False
            return
        engine.surface.blit(self.overlay,[0,0])
            
        angle = 3*(2*math.pi/4.0)
        max_angle = 2*math.pi
        diff_angle = max_angle/float(len(self.options))
        
        for option in self.options:
            dx,dy = self.radius*math.cos(angle),self.radius*math.sin(angle)
            center_pos = [self.pos[0]-offset[0],self.pos[1]-offset[1]]
            center_pos[0]+=dx
            center_pos[1]+=dy
            r = option.rect()
            center_pos[0]-=r.width//2
            center_pos[1]-=r.height//2
            option.pos = center_pos
            option.draw(engine)
            angle += diff_angle
    def rotate_right(self):
        self.options.append(self.options.pop(0))
    def rotate_left(self):
        self.options.insert(0,self.options.pop(-1))
    def setup(self,options,pause=True):
        self.radius = 0
        self.options = []
        for option_text,option_command,option_args in options:
            t = Text()
            t.set_text(option_text)
            t.command = option_command
            t.args = option_args
            self.options.append(t)
        self.enable()
        self.pause = pause
    def enable(self):
        self.world.engine.play_sound("mario_bounce")
        self.visible = True
    def disable(self):
        self.visible = False
    def action(self):
        self.disable()
        o = self.options[0]
        if hasattr(o,"command"):
            o.command(*o.args)

class Textbox(Agent):
    def init(self):
        self.text = Text()
        self.text.color = [255,255,255]
        self.text.font = "bigfont"
        self.said = ""
        self.to_say = "   "
        self.layer = 11
        self.finished = False
    def update(self,world):
        self.pos = [0,255]
        if len(self.said)<len(self.to_say):
            self.said = self.to_say[:len(self.said)+1]
            self.text.text = self.said
            self.text.surface = None
        else:
            self.finished = True
    def draw(self,engine,offset=[0,0]):
        self.text.draw(engine)
        
class PopupText(Text):
    def init(self):
        super(PopupText,self).init()
        self.timeout = 90
        self.layer = 11
        self.focus = None
        self.amt = 0
    def update(self,world):
        super(PopupText,self).update(world)
        self.timeout -= 1
        self.amt+=1
        self.pos = self.focus.pos[:]
        self.pos[1]-=self.amt
        if self.timeout<0:
            self.kill = 1