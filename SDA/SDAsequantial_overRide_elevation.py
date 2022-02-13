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
# import API.depth as depth


# import Agent as agents
# import SmellSpot as ss

class Agent:
    def __init__(self, name, total, current):
        self.name = name
        self.total = total
        self.current = current
        #adding
        self.route = [current]
        # self.score = 0
        self.cumulative_depth = 0
        
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
    
    # def save(self, value):
    #     self.data = value
        
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
        self.N_sda =  100 # number of sda 
        #if you'd like to use full cpu -> ' os.cpu_count()'
        
        self.N_ss = self.len  # number of smell spots
        self.N_limit = 50 # the number of who can each the destination
        self.a = 10  # init smell values
        self.b = 1 # Decrease Constant
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
                 self.ss[i].smellvalue = -math.inf
            if self.node[i] == self.destination :
                 self.ss[i].visitor = 'Agent in goal >> '
                
                
        self.color_map = [ 'black' for i in range(self.len )]    
        
        """ API data , you use or not"""
        self.considerFlood = False
        self.considerElevation = False
        
        # self.main()
        
        
        
        
    """    
    def distance(self, _from, to):
        return math.dist(self.pos[_from], self.pos[to])
    """
    
    def distance(self, _from):
        return math.dist(self.pos[_from], self.pos[self.destination])
    
    def distance3D(self, _from, next):
        dest = self.elevation.get(next)
        target = self.elevation.get(_from)
        straight =  math.dist(self.pos[_from], self.pos[next])
        # Pythagorean theorem
        return math.sqrt(straight**2 + (dest - target)**2 )
    
    
    def action(self, number):
        
        if self.lost == self.N_sda:
            print("- We can't arrive ...")
            self.agents[number].total = math.inf
            self.plot()
        elif self.arrived >= self.N_limit:
                self.agents[number].total = math.inf
        else:
            while(self.arrived < self.N_limit ):
                
                # time.sleep(random.random()/1000)
                # print('go')
                neighbors = self.getNeighbors(number)
                
                if self.agents[number].current == self.destination:
                    self.arrived += 1
                    # pprint.pprint(self.agents[number])
                    # print("- I am just arrived destination now")
                    # self.leave(self.agents[number].route)
                    break
                
                if len(neighbors ) == 0:
                    # pprint.pprint(self.agents[number])
                    print("- I can't arrive ...")
                    self.agents[number].total = math.inf
                    """
                    myloot = self.agents[number].route
                    myloot.pop()
                    self.leave(myloot)
                    """
                    # self.deadEnd(myloot)
                    # self.plot()

                    self.lost += 1
                    # self.N_sda += 1
                    break
                
                self.setSmelValue(number, neighbors)
                next = self.nextSmellSpot(neighbors)
                self.move(number, next)
                
                
                
        if  self.agents[number].current != self.destination:
            self.agents[number].total = math.inf
        
        
        self.ValueDown(self.agents[number].route)
    
        return  self.agents[number].current
    
    def leave(self, nodes):
        
        #messy
        for node in nodes:
            for i in range(len(self.ss)):
                if self.ss[i].nodeName == node:
                    self.ss[i].visitor = 'none'
                    self.ss[i].visitorTotal = math.inf
                    # print('delete')
                       
                    
                    
    def deadEnd(self, nodes):
        nodes = reversed(nodes)
        keep = True
        for node in nodes:
            for i in range(len(self.ss)):
                if self.ss[i].nodeName == node:
                    if keep and len(list(self.G.neighbors(node))) < 2:
                        self.ss[i].visitor = 'dead'
                        self.ss[i].smellvalue = 0
                        print('delete')
                    else:
                        keep = False

    def getNeighbors(self, num):
        indexList = []
        neighbors = list(self.G.neighbors(self.agents[num].current))
        for nb in neighbors: 
            for i in range(len(self.ss)):
                if  self.ss[i].nodeName == nb and self.ss[i].nodeName != self.source:
                    # expectTotal = self.agents[num].total + self.G[ self.agents[num].current][self.ss[i].nodeName ]['weight']
                    if (self.ss[i].visitor != self.agents[num].name): #自分が通った経路ではない
                        indexList.append(i)
                    
                    """
                    if (self.ss[i].visitor == 'none') or (self.ss[i].nodeName == self.destination) or (expectTotal <= self.ss[i].visitorTotal):
                        indexList.append(i)
                        
                        # if((expectTotal < self.ss[i].visitorTotal)):
                            # time.sleep(random.random()/1000)
                        #     # time.sleep(0.0001)
                            # print("expect!!")
                            # print(self.agents[num])
                        # # permit overRide
                    """
        return indexList
    
    
    def nextSmellSpot(self, nbs):
        max = 0
        maxIndex = 0
        
        # nbs.remove(self.source)
        for i in nbs:
            # if self.ss[i].visitor != 'none':
            #     maxIndex = i
            if self.ss[i].nodeName == self.destination:
                maxIndex = i
                break
            elif max < self.ss[i].smellvalue:
                max = self.ss[i].smellvalue
                maxIndex = i
        return maxIndex 
    
    
    def setSmelValue(self, num, nbs):
        for i in nbs:
            if self.ss[i].visitor == 'none':
                rate = 1
                
                if self.considerFlood:
                    """ parameter of flood and subject """
                    safe_level = 0.5 # 1-0
                    target_rate = 0.3 * safe_level
                    rate = self.depth.get(self.ss[i].nodeName)*target_rate + 1
                           
                else:
                    if self.considerElevation:
                        p = self.distance3D(self.ss[i].nodeName, self.destination) 
                    else:
                        p = self.distance(self.ss[i].nodeName)
                    
                self.ss[i].smellvalue =  1 / (self.a + self.b * p * rate ) 
                
                if self.ss[i].nodeName == self.source:
                    self.ss[i].smellvalue = 0 
                    
                
                
                
    
    def move(self, num, next):
        #new struct
        self.ss[next].visitorTotal = self.agents[num].total
        
        if self.considerFlood: 
            if len(list(self.G.neighbors(self.ss[next].nodeName))) > 2:
                self.agents[num].cumulative_depth += ( self.depth.get(self.ss[next].nodeName) ) #** 5
                # print(self.agents[num].cumulative_depth)
        
        if self.considerElevation:
            #distance 3D:
            self.agents[num].total += self.distance3D(self.agents[num].current, self.ss[next].nodeName )
        else:
            self.agents[num].total += self.G[ self.agents[num].current][self.ss[next].nodeName ]['weight'] 
        
        # self.agents[num].cumulative_depth += self.ss[next].data
        self.agents[num].route.append(self.ss[next].nodeName)
    
        self.agents[num].current = self.ss[next].nodeName
        if self.ss[next].nodeName == self.destination:
            self.ss[next].visitor += (str(self.agents[num].name) + ' ')
        else:
            self.ss[next].visitor = self.agents[num].name

            
    def main(self):
        max_workers = self.N_sda
        futureList = []
    
        """
        # when max_workers = None, it means max_workers = 5*os.cpu_count()
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="thread") as executor:
        # In using 'ProcessPoolExecutor' case, each process would be proceeded by order. ===> BUT, this method can't share a memory so it would be cause of bug.
        # with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for i in range(self.N_sda):
                future = executor.submit(self.action, i)
                futureList.append(future)
                if future == self.destination:
                    print('Goal')
                
            # print([x.result() for x in futureList])
        """    
            
        for i in range(self.N_sda):
            self.action(i)
            
        # """
        

        self.BestAgent = min(self.agents, key=lambda x: x.total)
        self.BestScore =  self.BestAgent.total
        
        # print(self.BestAgent)
        self.sorted = self.sortAgent()

    
        
        if self.BestScore==0:
            print(self.agents)
            

        
        # """
        for u,v in self.G.edges():
            self.G[u][v]["color"] = "black"
        

        if self.considerFlood:
            print("flood")
            sorted = self.safety()
        else:    
            sorted = self.sortAgent()
            print(sorted[0])
    
            
        self.nodeColor('red', sorted[0].route)
        self.edgeColor('red', sorted[0].route)
        # self.nodeColor('orange', sorted[1].route)
        # self.edgeColor('orange', sorted[1].route)
        # self.nodeColor('green', sorted[2].route)
        # self.edgeColor('green', sorted[2].route)

        
        
        
        self.edge_color = [edge["color"] for edge in self.G.edges.values()]
        # """
        
        # if self.BestScore == math.inf:
        #     self.plot()
    def select(self):
        # score
        for i in range(len(self.agents)):
            self.agents[i].score = self.agents[i].total * ( 1 + self.agents[i].cumulative_depth)
            
    
        
        
    def plot(self, node_size = None, with_labels=True):
        nx.draw(self.G, self.pos, node_size = node_size, node_color=self.color_map, with_labels=with_labels ,  edge_color=self.edge_color)
        plt.show()
        
    def answer(self):
        print("SDA-Algorithm Best Path >> ")
        self.output(self.BestAgent)
        
    def output(self, target ):
        print(target.name)
        print(target.total)
        print(target.route)
        
    def sortAgent(self):
        return sorted(self.agents, key=lambda x: x.total)
    
    def nodeColor(self, color, nodes):
        graph = list(self.G.nodes())
        for n in self.G:
            if n in nodes:
                self.color_map[graph.index(n)] = color
                
    def edgeColor(self, color, edges):
        for i in range(len(edges)-1):
            self.G[edges[i]][edges[i+1]]["color"] = color
                
    def ValueDown(self, route):
        decrease = 0.00001
        nearSource = list(self.G.neighbors(self.source))
        
        for node in route:
             for i in range(len(self.ss)):
                
                 if self.ss[i].nodeName == node and self.ss[i].nodeName != self.destination and self.ss[i].nodeName != self.source and self.ss[i].nodeName not in nearSource:
                    # self.ss[i].smellvalue = self.ss[i].smellvalue*(1-decrease*(1-self.ss[i].smellvalue))
                    self.ss[i].smellvalue = self.ss[i].smellvalue*(1-decrease)
                    
                    if self.considerFlood:
                        self.ss[i].smellvalue = self.ss[i].smellvalue* (1 - decrease* (1 + self.depth.get(self.ss[i].nodeName)) )
                
                    
    def getSmellSpot(self):
        pprint.pprint(self.ss)
        return self.ss
                     
    def flood(self, depth):
        self.depth = depth
        self.considerFlood = True
        
        # return 0
    
    def elevation(self, elevation):
        self.elevation = elevation
        self.considerEvelation = True
        
        # return 0
    
    def plotFlood(self, depth):
        
        return
    
    def safety(self):
        safetyAgents = sorted(self.agents, key=lambda x: x.cumulative_depth)
        
        print("SAFE")
        
        
        
        # for i in range(len(safetyAgents)):
        #     if safetyAgents[i].total == math.inf:    
                
        safetyAgents = [ agent for agent in safetyAgents if agent.total  != math.inf]
        
        safetyAgents = sorted(safetyAgents, key=lambda x: (x.cumulative_depth / len(x.route) ) / ( 1 + x.total )) 
    
        print(safetyAgents)
        
        return  safetyAgents
    
            
       
        
        # print(self.pos)
                              
    # def overRide(self):