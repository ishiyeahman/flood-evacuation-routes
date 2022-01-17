# module import error

import pickle
import API.depth as depth
import tqdm


FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/venv/SDA/data/Sagara/"
WHERE = "Sagara_Hitoyoshi"
PATH = FILE + WHERE

#get position of nodes
with open(f'{PATH}_pos.pkl', 'rb') as f:
    pos = pickle.load(f)
    
node = list(pos)

dict_Depth = {}

for i in tqdm.tqdm(range(len(node))):
# for i in range(20):
    lon, lat = pos.get(node[i])
    d = depth.get(lat, lon)
    new = {node[i] : d}
    dict_Depth.update(new)
    

print(dict_Depth)

with open(f'{PATH}_depth.pkl', 'wb') as f:
    pickle.dump(dict_Depth, f)
      
    
        
    



