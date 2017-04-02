from flask import Flask, render_template, request, redirect, url_for
from base64 import b64encode, b64decode
from markets import *
from flask_socketio import SocketIO, emit
from random import sample
import sqlite3

async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
data = get_markets()

c = sqlite3.connect('/home/saeveritt/Documents/tbarchive.db')
cur = c.cursor()
tbdata = []

def background_thread():
    global data, tbdata
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        count += 1
        cur.execute("SELECT name,msg,time from trollbox ORDER BY id DESC LIMIT 200 ")
        tbdata = cur.fetchall()
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

@app.route('/tbarchive/', methods=['GET','POST'])
def tbarchive():
    global tbdata
    value = request.form.get('search')
    option = request.form.get('option')
    if (option is not None) and value:
        value = b64encode(value.replace('"','&apos;').encode()).decode()
        return redirect(url_for('tbuser',option=option,value=value))
    return render_template("tbarchive.html",tbdata=tbdata)

@app.route('/tbarchive/<option>/<value>',methods=['GET','POST'])
def tbuser(option,value):
    global tbdata
    value = b64decode(value.encode()).decode().replace('&apos;','"')

    if option == 'msg':
        cur.execute("SELECT name,msg,time from trollbox WHERE msg LIKE '%{}%' ORDER BY id DESC LIMIT 200".format(value))
        _tbdata = cur.fetchall()
    elif option == 'name':
        cur.execute("SELECT name,msg,time from trollbox WHERE name == '{}' ORDER BY id DESC LIMIT 200".format(value))
        _tbdata = cur.fetchall()
    
    
    _value = request.form.get('search')
    _option = request.form.get('option')

    if (_option is not None):
        if _value is not None:
            _value = b64encode(_value.replace('"','&apos;').encode()).decode()
            if (_option == 'msg'):
                return redirect(url_for('tbuser',option=_option,value=_value))

            if (_option == 'name'):
                return redirect(url_for('tbuser',option=_option,value=_value))
        
        else:
            return render_template("tbarchive.html",tbdata=tbdata)
    return render_template("tbarchive.html",tbdata=_tbdata)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')
    
    
@socketio.on('tbsearch',namespace='/test')
def tbsearch(data):
    tboption(data)
    
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
