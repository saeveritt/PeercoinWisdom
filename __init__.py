from flask import Flask, render_template, request
from urllib.request import urlopen
from json import loads
from cryptotik import Btce
from pypeerassets.kutil import Kutil
from flask_socketio import SocketIO, emit
from random import sample
from hashlib import sha256

async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
data = {}

def get_markets():
    global data
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


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        count += 1
        data = get_markets()
        socketio.emit('update_table', data ,namespace='/test')
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')
        socketio.sleep(5)
        


@app.route("/")
def main():
    get_markets() 
    return render_template("index.html")

@socketio.on('generate', namespace='/test')
def generate():
    wordlist = open('bank.txt').read().split()
    words = [wordlist[i] for i in sample(range(0,len(wordlist)),12)]
    sentence = words[0]+ ' ' + ' '.join(words[1:])
    privkey = sha256(sentence.encode()).hexdigest()
    key = ""
    pubkey = ""
    address = ""
    emit('key',{"privkey":privkey, "pubkey":pubkey, "sentence": sentence, "address":address})

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
