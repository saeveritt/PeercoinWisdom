try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
    
from json import loads

def get_markets():
    data = {}
    market_ids = {"peercoin","bitcoin","litecoin","ethereum","dash","novacoin","namecoin"}
    markets = loads(urlopen('https://api.coinmarketcap.com/v1/ticker/?limit=100').read().decode())
    for i in markets:
        if i["id"] in market_ids:
            i["volume"] = i["24h_volume_usd"]
            i["available_supply"] = int(i["available_supply"].rstrip('.0'))
            del i["24h_volume_usd"]
            data[i["id"]] = i
    return data