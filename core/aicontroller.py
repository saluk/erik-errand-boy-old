import random

class AIController(object):
    def __init__(self,agent):
        self.agent = agent
    def control(self):
        a = self.agent
        a.idle()
        if a.following:
            self.follow()
        else:
            a.next_random_point-=1
            if a.next_random_point<=0:
                a.last_random_point = [a.pos[0]+random.randint(-100,100),a.pos[1]+random.randint(-100,100)]
                a.next_random_point = random.randint(200,400)
            self.walk_toward(self.agent.last_random_point)
    def follow(self):
        a = self.agent
        md = 8
        fp=8
        max = 10
        p = [a.following.pos[0]//fp*fp,a.following.pos[1]//fp*fp]
        if not a.following_points:
            a.following_points.append(p)
        if p!=a.following_points[-1] and a.following.map==a.map:
            a.following_points.append(p)
        if len(a.following_points)<5 and a.following.map==a.map:
            return
        if len(a.following_points)>max:
            a.following_points = a.following_points[-max:]
        p = a.following_points[0]
        if self.walk_toward(p):
            del a.following_points[0]
    def walk_toward(self,p):
        self = self.agent
        md = 8
        if abs(self.pos[0]-p[0])<=md and abs(self.pos[1]-p[1])<=md:
            return True
        if self.pos[1]-p[1]>md:
            self.up()
        elif self.pos[1]-p[1]<-md:
            self.down()
        if self.pos[0]-p[0]>md:
            self.left()
        elif self.pos[0]-p[0]<-md:
            self.right()