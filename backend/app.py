from flask import Flask, render_template, Response
import cv2
import time
import math
import smbus
import signal
import sys

class PCA9685:

  __MODE1              = 0x00
  __MODE2              = 0x01
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = int(pulse*4096/20000)        #PWM frequency is 50HZ,the period is 20000us
    self.setPWM(channel, 0, pulse)
    
  def start_PCA9685(self):
    self.write(self.__MODE2, 0x04)
    #Just restore the stopped state that should be set for exit_PCA9685
    
  def exit_PCA9685(self):
    self.write(self.__MODE2, 0x00)#Please use initialization or __MODE2 =0x04

  def set_rotation_angle(self, channel, angle):
    if angle > 180 or angle < 0:
      print("angle out of bounds")
    else:
      self.setServoPulse(channel, angle * (2000/180) + 500)

  def pan(self, pan_norm):
    self.set_rotation_angle(1, pan_norm * 180)

  def tilt(self, tilt_norm):
    self.set_rotation_angle(0, 5 + tilt_norm * 90) # min=5, max=95

pwm = PCA9685(0x40, debug=True)
pwm.setPWMFreq(50)
pwm.start_PCA9685()

"""
while True:
    for i in range(0, 100):  
        pwm.pan(i/100)   
        time.sleep(0.02)
    for i in range(0, 100):
        pwm.tilt(i/100) 
        time.sleep(0.02)
"""

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
  i = 0
  while True:
    # Capture frame-by-frame
    success, frame = camera.read()  # read the camera frame
    if not success:
      break
    else:
      ret, buffer = cv2.imencode(".jpg", frame)
      frame = buffer.tobytes()
      yield (b"--frame\r\n"
              b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")  # concat frame one by one and show result


@app.route("/video_feed")
def video_feed():
  #Video streaming route. Put this in the src attribute of an img tag
  return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def index():
  """Video streaming home page."""
  return render_template("index.html")

# http://exploreflask.com/en/latest/views.html#url-converters
@app.route("/pos/<float:pan>/<float:tilt>")
def pos(pan, tilt):
  pwm.pan(pan)
  pwm.tilt(tilt)
  return ("", 204)
