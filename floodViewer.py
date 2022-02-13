import flood.DepthView as dview
import networkx as nx

from setting import GRAPH, POS, LABEL, DEPTH 



G = dview.Graph(GRAPH, POS, LABEL,DEPTH)
G.plot()

