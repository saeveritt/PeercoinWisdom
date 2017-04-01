from flask import Flask, render_template, request
from markets import *
from flask_socketio import SocketIO, emit
from random import sample
from hashlib import sha256

async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
data = get_markets()


def background_thread():
    global data
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
    global data
    return render_template("index.html",data=data)

@app.route('/chart/<exchange>/<pair>')
def chartpage(exchange,pair):
    return render_template("charts.html",exchange=exchange,pair=pair)


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
