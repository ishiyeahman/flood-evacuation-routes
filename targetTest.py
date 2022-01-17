import pickle
import networkx as nx
import matplotlib.pyplot as plt
import csv

# -- smell detection agent based algorithm --
import SDAsequential_overRide as sda
# import SDAparallel_overRide as sda


FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/venv/SDA/data/Sagara/"
WHERE = "Sagara_Hitoyoshi"
PATH = FILE + WHERE



#get position of nodes
with open(f'{PATH}_pos.pkl', 'rb') as f:
    pos = pickle.load(f)

#view the list
G = nx.read_edgelist(f"{PATH}.edgelist", data=(("weight", float),))
# nx.draw(Gr, new_pos, node_size = 0.1)
# plt.show()

# get source and target
with open(f'{FILE}osm.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
    source , target = str(int(l[0][0])), str(int(l[0][1]))
    print(source , target)
    
nodeLabel = list(G.nodes)
   
# print(nodeLabel) 
# """
s = sda.Algorithm(G, pos, source, target, nodeLabel)
print(s.BestScore)
# nx.draw(G, pos, node_size = 0.1)
# plt.shows()



 

 
    # print(s.sortAgent())
s.plot(0.1, None)
# """