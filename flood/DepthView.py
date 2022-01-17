import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, G, pos,nodeLabel, depth = None):
        self.G = G
        self.pos = pos
        self.nodeLabel = nodeLabel
        self.depth = depth
        
        self.color_map = [ (0.3,0.4,0.5) for i in range(len(self.G) )]    
        self.node_size = 10
        
        
    def plot(self):
        # self.size()
        self.color()
        nx.draw(self.G, self.pos, node_size = self.node_size, node_color=self.color_map)
        plt.show()
        
    def color(self):
        self.color_map = []
        for i in range(len(self.nodeLabel)):
            d = self.depth.get(self.nodeLabel[i])
            self.color_map.append( (0 , 0, 1, 3*d/50 ) )
        
        
    def size(self):
        self.node_size = []
        for i in range(len(self.nodeLabel)):
            d = self.depth.get(self.nodeLabel[i])
            self.node_size.append( (d**3))
            
            