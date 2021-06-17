import RPi.GPIO as GPIO
import time
import threading
import sys

class HX711:

    def __init__(self, SCK,SDA,coefficient=415):
        self.SCK = SCK
        self.SDA = SDA
        #self.EN = 1
        self.calibration = 226280
        self.coefficient = coefficient
        self.value = 0
        self.weight = 0

        # Mutex for reading from the HX711, in case multiple threads in client
        # software try to access get values from the class at the same time.
        self.readLock = threading.Lock()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.SDA, GPIO.IN,pull_up_down=GPIO.PUD_UP)

    def read(self):
        self.readLock.acquire()
        GPIO.output(self.SCK,False)
        while(GPIO.input(self.SCK)):
            time.sleep(0.01)
        self.value = 0
        while(GPIO.input(self.SDA)):
            time.sleep(0.01)
        time.sleep(0.1)
        
        for i in range(0,24):
            GPIO.output(self.SCK,True)
            while(GPIO.input(self.SCK)==False):
                time.sleep(1)     
            self.value = self.value*2;
            GPIO.output(self.SCK,False)
            while(GPIO.input(self.SCK)):
                time.sleep(0.01)
            if  GPIO.input(self.SDA):
                self.value = self.value+1
                
        GPIO.output(self.SCK,True)        
        GPIO.output(self.SCK,False)
        time.sleep(0.01)
        self.readLock.release()           
        
        #if self.EN == 1:
           # self.EN = 0
           # self.calibration = self.value
            #return self.calibration
        #else:
        temp = (int)((self.value-self.calibration+50)/self.coefficient)
        if temp<0:
            self.weight=0
        elif temp>500:
            temp=500
        else:
            self.weight=temp
            #print("The weight is",self.weight,"g")
        return self.weight
 
    def power_down(self):
        # Wait for and get the Read Lock, incase another thread is already
        # driving the HX711 serial interface.
        self.readLock.acquire()

        # Cause a rising edge on HX711 Digital Serial Clock (PD_SCK).  We then
        # leave it held up and wait 100 us.  After 60us the HX711 should be
        # powered down.
        GPIO.output(self.SCK, False)
        GPIO.output(self.SCK, True)

        time.sleep(0.0001)

        # Release the Read Lock, now that we've finished driving the HX711
        # serial interface.
        self.readLock.release()           


    def power_up(self):
        # Wait for and get the Read Lock, incase another thread is already
        # driving the HX711 serial interface.
        self.readLock.acquire()

        # Lower the HX711 Digital Serial Clock (PD_SCK) line.
        GPIO.output(self.SCK, False)

        # Wait 100 us for the HX711 to power back up.
        time.sleep(0.0001)

        # Release the Read Lock, now that we've finished driving the HX711
        # serial interface.
        self.readLock.release()

        # HX711 will now be defaulted to Channel A with gain of 128.  If this
        # isn't what client software has requested from us, take a sample and
        # throw it away, so that next sample from the HX711 will be from the
        # correct channel/gain.
        #if self.get_gain() != 128:
            #self.readRawBytes()


    def reset(self):
        self.power_down()
        self.power_up()
        
'''
hx=HX711(5,6)
hx.reset()
while True:
    try:
        weight=hx.read()
        print("The weight is",weight,"g")
        time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        print("Cleaning...")
        GPIO.cleanup()
        print("Bye!")
        sys.exit()
'''
