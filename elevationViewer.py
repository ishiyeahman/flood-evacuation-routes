import elevation.ElevationView as eview
import networkx as nx

from setting import GRAPH, POS, LABEL, ELEVATION



G = eview.Graph(GRAPH, POS, LABEL, ELEVATION)
G.plot()

