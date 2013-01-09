import pygame
from tiledtmxloader import tmxreader
from agents import Agent

class Tile(Agent):
    def init(self):
        pass
    def is_empty(self):
        return self.index==-1
    def draw(self,engine,offset):
        super(Tile,self).draw(engine,offset)
        if hasattr(self,"chest"):
            s = pygame.Surface([32,32])
            s.fill([255,255,255])
            s.set_alpha(50)
            engine.surface.blit(s,[self.pos[0]-offset[0],self.pos[1]-offset[1]])
        
class TileLayer(Agent):
    def init(self):
        self.tiles = []
    def draw(self,engine,offset):
        for row in self.tiles:
            for tile in row:
                tile.draw(engine,offset)

class TileMap(Agent):
    def load(self,map):
        self.mapfile = map
        self.raw_map = tmxreader.TileMapParser().parse_decode(self.mapfile)

        self.tileset_list = [None]
        self.tile_properties = {}
        for tileset_raw in self.raw_map.tile_sets:
            props = {}
            for tile in tileset_raw.tiles:
                props[tile.id] = tile.properties
            tileset = pygame.image.load(tileset_raw.images[0].source).convert_alpha()
            x = 0
            y = 0
            i = 0
            while y*32<tileset.get_height():
                self.tileset_list.append(tileset.subsurface([[x*32,y*32],[32,32]]))
                if str(i) in props:
                    self.tile_properties[len(self.tileset_list)-1] = props[str(i)]
                i += 1
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
                for k,v in self.tile_properties.get(ti,{}).items():
                    setattr(tile,k,v)
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
        x,y = [i//32 for i in agent.pos]
        if x<0 or y<0 or x>=self.map_width or y>=self.map_height:
            return 1
        col = 0
        points =[(x,y)]
        for point in points:
            if self.collisions[point[1]][point[0]].index>0:
                return 1
    def get_sprites(self):
        return [layer for layer in self.map]