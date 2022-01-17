import networkx as nx
import matplotlib.pyplot as plt
import math
from concurrent.futures import ThreadPoolExecutor
# from concurrent.futures import ProcessPoolExecutor
from concurrent import futures
import pprint
import time
import random
from networkx.classes import graph

# import Agent as agents
# import SmellSpot as ss

class Agent:
    def __init__(self, name, total, current):
        self.name = name
        self.total = total
        self.current = current
        #adding
        self.root = [current]
        
    def __repr__(self):
        return self.__class__.__name__ + pprint.pformat(self.__dict__)  
        
class SmellSpot:
    def __init__(self, nodeName, visitor, smellvalue):
        self.nodeName = nodeName
        self.visitor = visitor
        self.smellvalue = smellvalue
        self.visitorTotal = math.inf
        
    def __repr__(self):
        return self.__class__.__name__ + pprint.pformat(self.__dict__)  
        
class Algorithm:
    def __init__(self, G, pos, source, destination, node):
        """ Graph data"""
        self.G = G
        self.pos = pos
        self.len = len(G)
        self.source = source
        self.destination = destination
        self.node = node

        """ Agent data"""
        self.N_sda =  8 # number of sda 
        #if you'd like to use full cpu -> ' os.cpu_count()'
        
        self.N_ss = self.len  # number of smell spots
        self.N_limit = 8 # the number of who can each the destination
        self.a = 1  # init smell values
        self.b = 10 # Decrease Constant
        # self.r = self.distance()
        
        self.arrived = 0
        self.lost = 0 #the number is the agents that be lost
        self.adjacent = list(self.G.neighbors(self.destination))
        
        # agents setting
        self.agents = []
        for i in range(self.N_sda):
            self.agents.append(Agent(i , 0, self.source) )

        # smellspots setting
        self.ss = []
        for i in range(self.N_ss):
            self.ss.append(SmellSpot(self.node[i] , 'none', 'unknown') )
            if self.node[i] == self.source:
                 self.ss[i].visitor = 'init'
            if self.node[i] == self.destination :
                 self.ss[i].visitor = 'Agent in goal >> '
                
                
        self.color_map = [ 'lightblue' for i in range(self.len )]    
        self.main()
        
        
        
    """    
    def distance(self, _from, to):
        return math.dist(self.pos[_from], self.pos[to])
    """
    
    def distance(self, _from):
        return math.dist(self.pos[_from], self.pos[self.destination])
    
    
    def action(self, number):
        
        if self.lost == self.N_sda:
            # print("- We can't arrive ...")
            self.agents[number].total = math.inf
            self.plot()
        elif self.arrived >= self.N_limit:
                self.agents[number].total = math.inf
        else:
            while(self.arrived < self.N_limit ):
                
                # time.sleep(random.random()/1000)
                neighbors = self.getNeighbors(number)
                
                if len(neighbors ) == 0:
                    # pprint.pprint(self.agents[number])
                    # print("- I can't arrive ...")
                    self.agents[number].total = math.inf
                    self.lost += 1
                    break
                
                self.setSmelValue(number, neighbors)
                next = self.nextSmellSpot(neighbors)
                self.move(number, next)
                
                if self.agents[number].current == self.destination:
                    self.arrived += 1
                    # pprint.pprint(self.agents[number])
                    # print("- I am just arrived destination now")
                    break
                
        if  self.agents[number].current != self.destination:
            self.agents[number].total = math.inf
    
        return  self.agents[number]
                

    def getNeighbors(self, num):
        indexList = []
        neighbors = list(self.G.neighbors(self.agents[num].current))
        for nb in neighbors: 
            for i in range(len(self.ss)):
                if (self.ss[i].nodeName == nb):
                    expectTotal = self.agents[num].total + self.G[ self.agents[num].current][self.ss[i].nodeName ]['weight']
                    if (self.ss[i].visitor == 'none') or (self.ss[i].nodeName == self.destination) or (expectTotal < self.ss[i].visitorTotal):
                        indexList.append(i)
                        # if((expectTotal < self.ss[i].visitorTotal)):
                            # time.sleep(random.random()/1000)
                        #     # time.sleep(0.0001)
                            # print("expect!!")
                            # print(self.agents[num])
                        # # permit overRide
                    
        return indexList
    
    
    def nextSmellSpot(self, nbs):
        max = 0
        maxIndex = 0
        
        
        for i in nbs:
            # if self.ss[i].visitor != 'none':
            #     maxIndex = i
            if max < self.ss[i].smellvalue:
                max = self.ss[i].smellvalue
                maxIndex = i
                
    
                
        return maxIndex 
    
    
    def setSmelValue(self, num, nbs):
        for i in nbs:
            # p = self.distance(self.agents[num].current,  self.ss[i].nodeName)
            p = self.distance(self.ss[i].nodeName)
            # self.ss[i].smellvalue =  1 / (self.a + self.b * p)       
            self.ss[i].smellvalue = ( 1 / (self.a + self.b * p) )# /  (self.G[ self.agents[num].current][self.ss[i].nodeName ]['weight'])
            # self.ss[i].smellvalue =  ( 1 / (self.a + self.b * p) ) - self.G[ self.agents[num].current][self.ss[i].nodeName ]['weight']
            if self.ss[i].nodeName in self.adjacent:
                self.ss[i].smellvalue = 1 / self.G[ self.agents[num].current][self.ss[i].nodeName ]['weight']
                
    
    def move(self, num, next):
        #new struct
        self.ss[next].visitorTotal = self.agents[num].total
        
        self.agents[num].total += self.G[ self.agents[num].current][self.ss[next].nodeName ]['weight']
        self.agents[num].root.append(self.ss[next].nodeName)
    
        self.agents[num].current = self.ss[next].nodeName
        if self.ss[next].nodeName == self.destination:
            self.ss[next].visitor += (str(self.agents[num].name) + ' ')
        else:
            self.ss[next].visitor = self.agents[num].name

            
    def main(self):
        max_workers = self.N_sda
        futureList = []
        # when max_workers = None, it means max_workers = 5*os.cpu_count()
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="thread") as executor:
        # In using 'ProcessPoolExecutor' case, each process would be proceeded by order. ===> BUT, this method can't share a memory so it would be cause of bug.
        # with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for i in range(self.N_sda):
                future = executor.submit(self.action, i)
                futureList.append(future)
                
            # print([x.result() for x in futureList])

        self.BestAgent = min(self.agents, key=lambda x: x.total)
        self.BestScore =  self.BestAgent.total
        
        if self.BestScore==0:
            print(self.agents)
            
        self.nodeColor('red', self.BestAgent.root)
        
            
        # self.output()
        
    def plot(self):
        nx.draw(self.G, self.pos, node_color=self.color_map, with_labels=True)
        plt.show()
        
    def answer(self):
        print("SDA-Algorithm Best Path >> ")
        self.output(self.BestAgent)
        
    def output(self, target ):
        print(target.name)
        print(target.total)
        print(target.root)
        
    def sortAgent(self):
        return sorted(self.agents, key=lambda x: x.total)
    
    def nodeColor(self, color, nodes):
        graph = list(self.G.nodes())
        for n in self.G:
            if n in nodes:
                self.color_map[graph.index(n)] = color
                
                
    # def overRide(self):
        
            
        