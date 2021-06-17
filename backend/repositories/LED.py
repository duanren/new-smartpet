# pylint: skip-file
from RPi import GPIO
import time

class LED:

    def __init__(self, pins):
        self.leds=pins
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pins, GPIO.OUT)
        
        GPIO.output(self.leds,0)
        
    def show(self,num):
        num=int(num)
        if num <1 or num >3:
            print("LED ERROR")
            return 1
        
        for i in range(0,2):
            if i == num-1:
                GPIO.output(self.leds[i],1)
            else:
                GPIO.output(self.leds[i],0)
                
        return 0
'''
try:
    led=LED([4,17,27])
    while True:
        led.show(1)
        time.sleep(1)
        led.show(2)
        time.sleep(1)
        led.show(3)
        time.sleep(1)
except KeyboardInterrupt as e:
    print(e)
finally:
    GPIO.cleanup()
    print("Finish")
'''
                
                
            