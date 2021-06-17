# pylint: skip-file
from repositories.myDataRepository import DataRepository
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading

# Custom imports
from RPi import GPIO
from repositories.Servo import Servo
from repositories.myhx711 import HX711

# Start app
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartpet_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
thread = None
thread_lock = threading.Lock()

# pins
pin_servo = 21

pins_load_feed = [5, 6]

# def setup():
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

hx = HX711(pins_load_feed[0], pins_load_feed[1])
servo=Servo(pin_servo)

# data
settings = DataRepository.read_settings()
storage=settings['storage']
weight_set = 80
weight_now = 0
weight_last = 0
storage_warning = 500

namespace='/data'


@app.route('/')
@app.route('/myindex/')
def index():
    return render_template('myindex.html')

@app.route('/history', methods=['GET'])
def get_history():
    if request.method == 'GET':
       return render_template('myhistory.html')


@app.route('/history/day', methods=['GET'])
def get_history_day():
    if request.method == 'GET':
        s = DataRepository.read_history_day()
        return jsonify(s), 200


@app.route('/history/week', methods=['GET'])
def get_history_week():
    if request.method == 'GET':
        s = DataRepository.read_history_week()
        return jsonify(s), 200


@app.route('/history/month', methods=['GET'])
def get_history_month():
    if request.method == 'GET':
        s = DataRepository.read_history_month()
        return jsonify(s), 200


@app.route('/history/year', methods=['GET'])
def get_history_year():
    if request.method == 'GET':
        s = DataRepository.read_history_year()
        return jsonify(s), 200


@app.route('/history/date/<date>', methods=['GET'])
def get_history_date(date):
    if request.method == 'GET':
        s = DataRepository.read_history_date(date)
        return jsonify(s), 200


@app.route('/fillhistory/day', methods=['GET'])
def get_fillhistory_day():
    if request.method == 'GET':
        s = DataRepository.read_fillhistory_day()
        return jsonify(s), 200


@app.route('/feedaverage/<days>', methods=['GET'])
def get_feed_average(days):
    if request.method == 'GET':
        s = DataRepository.read_feed_average(days)
        return jsonify(s), 200


@app.route('/feedcount/<days>', methods=['GET'])
def get_feed_count_today(days):
    if request.method == 'GET':
        s = DataRepository.read_feed_count_today(days)
        return jsonify(s), 200


@app.route('/add_quantity', methods=['POST'])
def add_quantity():
    if request.method == 'POST':
        tempdata = DataRepository.json_or_formdata(request)
        data = DataRepository.add_quantity(
            tempdata['quantity'])

        return jsonify(data), 201


@app.route('/app_settings', methods=['GET', 'PUT'])
def app_settings():
    if request.method == 'GET':
      return render_template('mysettings.html')


@app.route('/measure', methods=['GET'])
def read_measure():
    if request.method == 'GET':
        s = DataRepository.read_measure()
        return jsonify(s), 200


@app.route('/changes', methods=['GET'])
def read_changes():
    if request.method == 'GET':
        s = DataRepository.read_changes()
        return jsonify(s), 200

# SOCKET IO


@socketio.on('connect',namespace=namespace)
def initial_connection():
    #print('A new client connect')
    # # Send to the client!
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=start_processen)


@socketio.on('F2B_read_settings',namespace=namespace)
def F2B_read_settings():
    socketio.emit('B2F_send_settings',{'daily_goal':settings['daily_goal'],'daily_range':settings['daily_range'],
                                       'storage':settings['storage']},namespace=namespace)


@socketio.on('F2B_change_settings',namespace=namespace)
def F2B_change_settings(data):
    global settings,storage
    Data = DataRepository.update_settings(data['new_goal'],data['new_range'],data['new_storage'])
    settings = DataRepository.read_settings()
    storage=settings['storage']
    socketio.emit('B2F_send_settings',{'daily_goal':settings['daily_goal'],'daily_range':settings['daily_range'],
                                       'storage':settings['storage']},namespace=namespace)

def read_history():
     s = DataRepository.read_history()
     q=[]
     m=[]
     for x in s:
        q.append(x['quantity'])
        m.append(x['measure_time'].strftime('%Y-%m-%d %H-%M-%S'))
     socketio.emit('B2F_history',{'quantity':q,'measure_time':m},namespace=namespace)
     
     
# ACTION
def fill():
    global weight_set, weight_now, weight_last,settings,storage

    weight_now=hx.read()
    weight_last=weight_now
    i = 0
    while(weight_now < weight_set):
        if(i%2 == 0):
            servo.start()
        else:
            servo.start_links()
       
        weight_now=hx.read()
        difference=weight_now-weight_last
        data=DataRepository.servo_on()
        print(f"last: {weight_last}g add:{difference}g now weight: {weight_now}g")
        data = DataRepository.storage_change(difference)
        weight_last=weight_now
        time.sleep(1)
        i += 1
    else:
        servo.stop()
        data=DataRepository.servo_off()
        weight_now=hx.read()
        weight_last=weight_now
        
         
        
def weight_read_feed_setup():
    global weight_now,weight_last
    hx.reset()
    
    weight_now=hx.read()
    weight_last=weight_now
    #threading.Timer(5,weight_read_feed).start()
    

def weight_read_feed():
    global weight_set, weight_now, weight_last,storage,settings
    
    weight_temp=hx.read()
    #print(weight_now)
    t = time.strftime('%H:%M:%S', time.localtime())
    difference=weight_temp-weight_last  # difference BETWEEN last VALUE
    if abs(difference)> 25 and abs(difference)<200:
        weight_now=weight_temp
        print(f"NOW:{weight_now}g difference: {difference}g")
        if difference < 0:# pet has eaten
            data=DataRepository.add_eaten(abs(difference))
    else:
        print(f"NOW:{weight_now}g")
        
    socketio.emit('B2F_report',{'time':t,'weight':weight_now,'storage':storage},namespace=namespace)
    read_history()
    #socketio.emit("B2F_storage_empty",namespace=namespace)
    weight_eaten_today=DataRepository.read_feed_today()
    if(weight_now < weight_set):
        if weight_eaten_today is not None:
            if(weight_eaten_today['sum_quantity'] < settings['daily_range']):
                fill()
            else:
                print("Too much eaten, feed is no longer automatically completed")
        else:
            fill()
            
    socketio.sleep(1)
            
    settings = DataRepository.read_settings()
    storage=settings['storage']
    if storage<storage_warning:
        socketio.emit("B2F_storage_empty",namespace=namespace)
    else:
        socketio.emit("B2F_storage_enough",namespace=namespace)    
       
        
    
    weight_now=hx.read()
    weight_last=weight_now
 

def start_processen():
    weight_read_feed_setup()
    while True:
        weight_read_feed()
        socketio.sleep(5)
    # threading.Timer(2,distance_measure).start() # wait with distance two seconds
    


if __name__ == '__main__':
    print("** SmartPET start **")       
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)

