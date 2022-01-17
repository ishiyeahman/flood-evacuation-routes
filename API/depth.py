import requests
import json

# latitude , longitude 
def get(LAT, LON):
    
    # Japan check LAT < LON
    if LAT > LON:
        print("this is not correct data. (In Japan) ")
        exit()
        
    url = f"https://suiboumap.gsi.go.jp/shinsuimap/Api/Public/GetMaxDepth?lon={LON}&lat={LAT}"
    response = requests.get(url)
    jsonData = response.json()

    # データの有無の確認
    if jsonData: 
        depth = jsonData["Depth"]
    else :
        depth = 0
        
    return depth

def saveData():
    return