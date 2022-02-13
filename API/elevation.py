import requests
import json

# latitude , longitude 
def get(LAT, LON):
    
    # Japan check LAT < LON
    if LAT > LON:
        print("this is not correct data. (In Japan) ")
        exit()
        
    url = f"https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lon={LON}&lat={LAT}&&outtype=JSON"
    response = requests.get(url)
    jsonData = response.json()

    # データの有無の確認
    if jsonData: 
        elevation = jsonData["elevation"]
    else :
        elevation = None
        
    return elevation

def saveData():
    return