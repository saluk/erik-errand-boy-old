import math

from agents import Agent

class Radial(Agent):
    def init(self):
        self.options = []
        self.radius = 60
    def draw(self,engine,offset=[0,0]):
        angle = 0
        max_angle = 2*math.pi
        diff_angle = max_angle/float(len(self.options))
        
        for option in self.options:
            dx,dy = self.radius*math.cos(angle),self.radius*math.sin(angle)
            print dx,dy
            center_pos = [self.pos[0]-offset[0],self.pos[1]-offset[1]]
            center_pos[0]+=dx
            center_pos[1]+=dy
            r = option.rect()
            center_pos[0]-=r.width//2
            center_pos[1]-=r.height//2
            option.pos = center_pos
            print "draw",option,center_pos
            option.draw(engine)
            angle += diff_angle