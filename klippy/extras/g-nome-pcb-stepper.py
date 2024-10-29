import wiringpi as wpi
from wiringpi import GPIO
import time

class OrangePiGPIO:
    def __init__(self, pin: int):
        self.__step_pin_num = pin
        self.setup_pins()
        
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(pin, GPIO.OUT)

    def setup_pins(self):
        print(wpi.PWM_OUTPUT)
        # wpi.wiringPiSetup()
        # wpi.pinMode(self.__step_pin_num, wpi.PWM_OUTPUT)
        # wpi.pwmSetMode(wpi.PWM_MODE_MS)
        # wpi.pwmSetClock(600)
        # wpi.pwmSetRange(255)
        wpi.wiringPiSetup()
        wpi.pinMode(self.__step_pin_num, wpi.OUTPUT)
        wpi.softPwmCreate(self.__step_pin_num, 0, 255)

    def set_pwm(self, val):
        if val > 255:
            val = 255
        wpi.softPwmWrite(self.__step_pin_num, val)
        
    # def set_pin(self, pin, state):
    #     GPIO.output(pin, state)

    # def cleanup(self):
    #     GPIO.cleanup()

if __name__ == '__main__':
    orangePi = OrangePiGPIO(2)
    orangePi.set_pwm(128)
    time.sleep(1)
    orangePi.set_pwm(0)
