#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Read directional graph from Open Street Maps osm format

Based on Loïc Messal's OSMParser.py: https://gist.github.com/Tofull/49fbb9f3661e376d2fe08c2e9d64320e
Use python3.6

"""
import matplotlib.pyplot as plt
import math
import copy
import networkx # 2.0
import xml.sax # parse osm file
from pathlib import Path # manage cached tiles


import pickle
import numpy as np

RE = 6378137.0  # GRS80
FE = 1/298.257223563  # IS-GPS
E2 = FE * (2 - FE)
DEGREE = math.pi / 180

def distance(u, v):
    p, q = u['pos'], v['pos']
    coslat = math.cos((p[1]+q[1])/2*DEGREE)
    w2 = 1 / (1 - E2 * (1 - coslat * coslat))
    dx = (p[0]-q[0]) * coslat
    dy = (p[1]-q[1]) * w2 * (1 - E2)
    return math.sqrt((dx*dx+dy*dy)*w2) * DEGREE * RE


def download_osm(left, bottom, right, top, proxy = False, proxyHost = "10.0.4.2", proxyPort = "3128", cache = False, cacheTempDir = "/tmp/tmpOSM/", verbose = True):
    """ Return a filehandle to the downloaded data from osm api."""

    import urllib.request # To request the web

    if (cache):
        ## cached tile filename
        cachedTileFilename = "osm_map_{:.8f}_{:.8f}_{:.8f}_{:.8f}.map".format(left, bottom, right, top)

        if (verbose):
            print("Cached tile filename :", cachedTileFilename)

        Path(cacheTempDir).mkdir(parents = True, exist_ok = True) ## Create cache path if not exists

        osmFile = Path(cacheTempDir + cachedTileFilename).resolve() ## Replace the relative cache folder path to absolute path

        if osmFile.is_file():
            # download from the cache folder
            if (verbose):
                print("Tile loaded from the cache folder.")

            fp = urllib.request.urlopen("file://"+str(osmFile))
            return fp

    if (proxy):
        # configure the urllib request with the proxy
        proxy_handler = urllib.request.ProxyHandler({'https': 'https://' + proxyHost + ":" + proxyPort, 'http': 'http://' + proxyHost + ":" + proxyPort})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)


    request = "http://api.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f"%(left,bottom,right,top)

    if (verbose):
        print("Download the tile from osm web api ... in progress")
        print("Request :", request)

    fp = urllib.request.urlopen(request)

    if (cache):
        if (verbose):
            print("Write osm tile in the cache")
        content = fp.read()
        with open(osmFile, 'wb') as f:
            f.write(content)

        if osmFile.is_file():
            if (verbose):
                print("OSM tile written in the cache")

            fp = urllib.request.urlopen("file://"+str(osmFile)) ## Reload the osm tile from the cache (because fp.read moved the cursor)
            return fp

    return fp


def read_osm(filename_or_stream, only_roads=True):
    """Read graph in OSM format from file specified by name or by stream object.
    Parameters
    ----------
    filename_or_stream : filename or stream object

    Returns
    -------
    G : Graph
    """
    osm = OSM(filename_or_stream)
    # G = networkx.DiGraph()
    G = networkx.Graph()

    ## Add ways
    for w in osm.ways.values():
        if only_roads and 'highway' not in w.tags:
            continue

        # G.add_path(w.nds, id=w.id)
        networkx.add_path(G, w.nds, id=w.id)
        # G.add_edge(w.nds, id=w.id)
        
        # reverse direction
        if ('oneway' not in w.tags) or (w.tags['oneway'] != 'yes'):
            # G.add_path(w.nds[::-1], id=w.id)
            networkx.add_path(G, w.nds[::-1], id=w.id)
            # G.add_edge(w.nds[::-1], id=w.id)

    ## Complete the used nodes' information
    for n_id in list(G.nodes):
        n = osm.nodes[n_id]
        G.nodes[n_id]['pos'] = [n.lon, n.lat]

    ## Estimate the length of each way
    for u,v in G.edges():
        d = distance(G.nodes[u], G.nodes[v])
        G.add_weighted_edges_from([(u, v, d)], weight='length')
    return G

class Node:
    def __init__(self, id, lon, lat):
        self.id = id
        self.lon = lon
        self.lat = lat
        self.tags = {}

    def __str__(self):
        return "Node (id : %s) lon : %s, lat : %s "%(self.id, self.lon, self.lat)

class Way:
    def __init__(self, id, osm):
        self.osm = osm
        self.id = id
        self.nds = []
        self.tags = {}

    def split(self, dividers):
        # slice the node-array using this nifty recursive function
        def slice_array(ar, dividers):
            for i in range(1,len(ar)-1):
                if dividers[ar[i]]>1:
                    left = ar[:i+1]
                    right = ar[i:]
                    rightsliced = slice_array(right, dividers)
                    return [left]+rightsliced
            return [ar]

        slices = slice_array(self.nds, dividers)

        # create a way object for each node-array slice
        ret = []
        i=0
        for slice in slices:
            littleway = copy.copy( self )
            littleway.id += "-%d"%i
            littleway.nds = slice
            ret.append( littleway )
            i += 1
        return ret

class OSM:
    def __init__(self, filename_or_stream):
        """ File can be either a filename or stream/file object."""
        nodes = {}
        ways = {}

        superself = self

        class OSMHandler(xml.sax.ContentHandler):
            @classmethod
            def setDocumentLocator(self,loc):
                pass

            @classmethod
            def startDocument(self):
                pass

            @classmethod
            def endDocument(self):
                pass

            @classmethod
            def startElement(self, name, attrs):
                if name=='node':
                    self.currElem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']))
                elif name=='way':
                    self.currElem = Way(attrs['id'], superself)
                elif name=='tag':
                    self.currElem.tags[attrs['k']] = attrs['v']
                elif name=='nd':
                    self.currElem.nds.append( attrs['ref'] )

            @classmethod
            def endElement(self,name):
                if name=='node':
                    nodes[self.currElem.id] = self.currElem
                elif name=='way':
                    ways[self.currElem.id] = self.currElem

            @classmethod
            def characters(self, chars):
                pass

        xml.sax.parse(filename_or_stream, OSMHandler)
        self.nodes = nodes
        self.ways = ways
        #count times each node is used
        node_histogram = dict.fromkeys( self.nodes.keys(), 0 )
        for way in self.ways.values():
            if len(way.nds) < 2:       #if a way has only one node, delete it out of the osm collection
                del self.ways[way.id]
            else:
                for node in way.nds:
                    node_histogram[node] += 1
        #use that histogram to split all ways, replacing the member set of ways
        new_ways = {}
        for _, way in self.ways.items():
            split_ways = way.split(node_histogram)
            for split_way in split_ways:
                new_ways[split_way.id] = split_way
        self.ways = new_ways

def transpose_list(list2d):
    return map(list, zip(*list2d)) 

def center_pos(G):
    pos = [G.nodes[n]['pos'] for n in G]
    lons, lats = tuple(transpose_list(pos))
    return [(min(lons)+max(lons))/2, (min(lats)+max(lats))/2]

def plot_osm(G, path=None):
    # import matplotlib.pyplot as plt
    coslat = math.cos(center_pos(G)[1]*DEGREE)
    ax = plt.figure().add_subplot(111)
    if path:
        ax.plot(*path, color='red', lw=1.6)
    for u, v in G.edges():
        e = transpose_list([G.nodes[u]['pos'], G.nodes[v]['pos']])
        ax.plot(*e, color='0.6', lw=0.5)
    ns = transpose_list([G.nodes[n]['pos'] for n in G])
    ax.plot(*ns, 'o', color='black', mec='none', ms=1.2)
    ax.grid(color='0.9')
    ax.set_aspect(1/coslat)
    plt.show()
    return

def main():
    WHERE = "Tsuboi-4-chome_Kumamotoshi"
  
    f = download_osm(130.7100, 32.8075, 130.7292, 32.8224)
    
    
    
    
    G = read_osm(f)

    source , target = '1516132490', '1516132726'
    dist = lambda u,v: distance(G.nodes[u],G.nodes[v])
    nodeLabel = list(G.nodes)
    pos = networkx.get_node_attributes(G,'pos')
    for i in nodeLabel:
        for j in nodeLabel:
            if j in G[i]:
                G[i][j]["weight"] = weight(i, j, pos)
    # print(networkx.get_node_attributes(G,'pos'))
    
   

    path = networkx.astar_path(G, source, target, heuristic=dist, weight='length')
    path = transpose_list([G.nodes[u]['pos'] for u in path])
    plot_osm(G, path)
    print(networkx.astar_path_length(G, source, target, heuristic=dist, weight='length'))
    
    # """
    networkx.write_edgelist(G, f"{WHERE}.edgelist", data=["weight"])
    #G = nx.read_edgelist("test.edgelist", nodetype=int, data=(("weight", float),))
    

    
    with open(f'{WHERE}_pos.pkl', 'wb') as f:
        pickle.dump(pos, f)
        
    with open(f'{WHERE}_pos.pkl', 'rb') as f:
        new_pos = pickle.load(f)
        
    Gr = networkx.read_edgelist(f"{WHERE}.edgelist", data=(("weight", float),))
    networkx.draw(Gr, new_pos, node_size = 0.1)
    plt.show()
    # """
    return

def weight(fr, to, pos): 
    return np.sqrt((pos[fr][0] - pos[to][0])** 2 + (pos[fr][1] - pos[to][1])** 2 )

    
    
if __name__ == '__main__':
    main()