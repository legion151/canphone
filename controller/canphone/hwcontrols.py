import threading
from gpiozero import LED, Button, Device, Pin
from gpiozero.pins.mock import MockFactory
from signal import pause
from time import sleep
from enum import Enum, auto
import logging
from rpi_ws281x import *

log = logging.getLogger("canphone")

# uncomment to run on PC hardware
#Device.pin_factory = MockFactory()


class CanState(Enum):
    LIFTED = auto()
    HUNGUP = auto()

class PttState(Enum):
    PRESSED = auto()
    RELEASED = auto()

class PhoneControls:
    def __init__(self,  callbPush, callbHang, ledPin = 17, pttPin = 18, canPin = 19):
        # define properties
        self.blinkThread = None
        self.led = LED(ledPin)
        self.pttButton = Device.pin_factory.pin(pttPin)
        self.canButton:Pin = Device.pin_factory.pin(canPin)
        # configure hardware
        self.__configPinHandler__(self.pttButton, self.__pttCallback__)
        self.__configPinHandler__(self.canButton, self.__canCallback__)
        self.cbCan = callbHang
        self.cbPtt = callbPush
        self.rgbled = Adafruit_NeoPixel(TOTAL_LED_COUNT, ledPin, 800000, 5, False, 255)

    def __configPinHandler__(self, button: Pin, cb):
        button.edges = "both"
        button.input_with_pull("up")
        button.bounce = .250
        button.when_changed = cb

    def __canCallback__(self, ticks, state):
        sleep(0.2)
        state = self.canButton.state
        log.debug("Can button state=%d", state)
        if state == 1:
            self.cbCan(CanState.HUNGUP)
        else:
            self.cbCan(CanState.LIFTED)

    def __pttCallback__(self, ticks, state):
        sleep(0.2)
        state = self.pttButton.state
        log.debug("PTT button state=%d", state)
        if state == 1:
            self.cbPtt(PttState.PRESSED)
        else:
            self.cbPtt(PttState.RELEASED)

    def startBlinking(self, R=255, G=255, B=255):
        self.stopBlinking()
        self.blinkThread = threading.Thread(target=self.__blinking__(self.R,self.G,self.B))
        self.blinkThread.start()

    def stopBlinking(self):
        if self.blinkThread != None:
            self.blinkThread._stop()
            self.blinkThread = None

    def __blinking__(self, R, G, B):
        log.debug("Starting blink loop.")
        while True:
            self.rgbled.begin()
            self.rgbled.setPixelColorRGB(0, self.R, self.G, self.B)
            self.rgbled.show()
            self.rgbled.setPixelColorRGB(0, 0, 0, 0)
            self.rgbled.show()
