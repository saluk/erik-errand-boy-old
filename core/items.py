import random

from agents import Agent

class Item(Agent):
    names = ["apple","bananna","handkerchief","gloves","axe","sword","bucket","ring","bracelet","knife","coins","note","booklet","glass","leaflet"]
    def init(self):
        names = Item.names[:]
        self.name = random.choice(names)