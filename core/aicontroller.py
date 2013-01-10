class AIController(object):
    def __init__(self,agent):
        self.agent = agent
    def control(self):
        a = self.agent
        a.idle()
        if a.following:
            self.follow()
    def follow(self):
        self = self.agent
        md = 8
        fp=8
        max = 10
        p = [self.following.pos[0]//fp*fp,self.following.pos[1]//fp*fp]
        if not self.following_points:
            self.following_points.append(p)
        if p!=self.following_points[-1] and self.following.map==self.map:
            self.following_points.append(p)
        if len(self.following_points)<5 and self.following.map==self.map:
            return
        if len(self.following_points)>max:
            self.following_points = self.following_points[-max:]
        p = self.following_points[0]
        if abs(self.pos[0]-p[0])<=md and abs(self.pos[1]-p[1])<=md:
            del self.following_points[0]
            return
        if self.pos[1]-p[1]>md:
            self.up()
        elif self.pos[1]-p[1]<-md:
            self.down()
        if self.pos[0]-p[0]>md:
            self.left()
        elif self.pos[0]-p[0]<-md:
            self.right()