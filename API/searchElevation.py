import pickle
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures as futures

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  
import elevation


# """
FILE = "/Volumes/GoogleDrive/マイドライブ/HI5/卒業研究/main/src/data/Tsuboi-4-chome/"
WHERE = "Tsuboi-4-chome_Kumamotoshi"
PATH = FILE + WHERE

#get position of nodes
with open(f'{PATH}_pos.pkl', 'rb') as f:
    pos = pickle.load(f)
    
node = list(pos)
dict_Elevation = {}
max_workers = 1000 


def process(i):
    # for i in range(20):
    lon, lat = pos.get(node[i])
    d = elevation.get(lat, lon)
    new = {node[i] : d}
    dict_Elevation.update(new)
    
    # print("proceed...", i)
    return d
    

    
if __name__ == '__main__':
    with tqdm(total=len(node)) as pbar:
        fs = []
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="thread") as executor:
            for i in range(len(node)):
                f = executor.submit(process, i)
                fs += [f]
            for f in futures.as_completed(fs):
                pbar.update(1)
            
    # with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="thread") as executor:
    #     for i in tqdm.tqdm(range(len(node))):
    #         future = executor.submit(process, i)
    #         futureList.append(future)
                
    print("file save ... ")
    with open(f'{PATH}_elevation.pkl', 'wb') as f:
        pickle.dump(dict_Elevation, f)
    print("End")   


# """