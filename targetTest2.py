import pickle
import networkx as nx
import matplotlib.pyplot as plt
import csv
# import DepthView as dview
from setting import GRAPH, POS, LABEL, DEPTH ,FILE, ELEVATION

# -- smell detection agent based algorithm --
import SDA.SDAsequantial_overRide_elevation as sda


with open(f'{FILE}osm.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
    source , target = str(int(l[0][0])), str(int(l[0][1]))
    

   
# print(nodeLabel) 
# """
s = sda.Algorithm(GRAPH, POS, source, target, LABEL)
# s.flood(DEPTH)
# s.elevation(ELEVATION)

s.main()

s.plot(0.1, None)
