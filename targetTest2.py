import pickle
import networkx as nx
import matplotlib.pyplot as plt
import csv
# import DepthView as dview

# -- smell detection agent based algorithm --
import SDA.SDAsequential_overRide as sda
# import SDAparallel_overRide as sda

# FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/venv/SDA/data/Sagara/"
FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/main/src/data/Shinyashiki-2-chome/"
# FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/venv/SDA/data/Shinyashiki-2-chome/"
WHERE = "Shinyashiki-2-chome_Kumamotoshi"
PATH = FILE + WHERE

#get position of nodes
with open(f'{PATH}_pos.pkl', 'rb') as f:
    pos = pickle.load(f)
    
#get infomation about water depth
with open(f'{PATH}_depth.pkl', 'rb') as f:
    depth = pickle.load(f)

#view the list
G = nx.read_edgelist(f"{PATH}.edgelist", data=(("weight", float),))
# nx.draw(Gr, new_pos, node_size = 0.1)
# plt.show()

# get source and target
with open(f'{FILE}osm.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
    source , target = str(int(l[0][0])), str(int(l[0][1]))
    
nodeLabel = list(G.nodes)
   
# print(nodeLabel) 
# """
s = sda.Algorithm(G, pos, source, target, nodeLabel)
s.flood(depth)
s.main()

s.plot(0.1, None)
# plt.shows()
 
    # print(s.sortAgent())

# """

# depthG = dview.Graph(G, pos, nodeLabel, depth)
# depthG.plot()