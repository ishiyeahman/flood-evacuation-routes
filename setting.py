"""
DO COPPY THIS IMPORT TEXT

---
if you want search routes under flood:
    import GRAPH, POS, LABEL, DEPTH from setting 
---
if you need the infomation about elevation 
    import GRAPH, POS, LABEL, DEPTH, ELEVATION from setting 
---
"""

import pickle
import networkx as nx
import csv

"""
FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/main/src/data/Tsuboi-4-chome/"
WHERE = "Tsuboi-4-chome_Kumamotoshi"
"""

FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/main/src/data/Shimoshiromoto/"
WHERE = "Shimoshiromoto_Hitoyoshi"

PATH = FILE + WHERE

""" Essential data """
with open(f'{PATH}_pos.pkl', 'rb') as f:
    POS = pickle.load(f)
    
with open(f'{FILE}osm.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
    SOURCE , TARGET = str(int(l[0][0])), str(int(l[0][1]))
    
GRAPH = nx.read_edgelist(f"{PATH}.edgelist", data=(("weight", float),))
LABEL = list(GRAPH.nodes)
  
""" API data """
with open(f'{PATH}_depth.pkl', 'rb') as f:
    DEPTH = pickle.load(f)
    
with open(f'{PATH}_elevation.pkl', 'rb') as f:
    ELEVATION = pickle.load(f)








    



