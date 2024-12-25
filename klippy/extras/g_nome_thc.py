import wiringpi as wpi
from wiringpi import GPIO
import threading
import time
import os
# import glob
import csv
import json


REPORT_TIME = 0.300
SAMPLE_TIME = 0.001
SAMPLE_COUNT = 8
# REPORT_TIME = 0.300

def sleep_microseconds(usec):
    # sec = usec // 1000000
    # remaining_usec = usec % 1000000
        
    # time.sleep(sec)
    # while remaining_usec > 0:
    #     time.sleep(0)  # Запускаем пустой таймаут
    #     remaining_usec -= time.clock() % 1000000
    # start = wpi.delayMicroseconds()
    pass

class THC_ADC:

    REPORT_TIME= 1.300  # seconds


    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()

        ppins = self.printer.lookup_object('pins')
        pin_name = config.get('sensor_pin')
        self.mcu_adc = ppins.setup_pin('adc', pin_name)
        self.mcu_adc.setup_adc_callback(REPORT_TIME, self.callback)
        self.mcu_adc.setup_adc_sample(SAMPLE_TIME, SAMPLE_COUNT)

        self.printer.register_event_handler("klippy:ready", self.__ready_event)
        pass

    def callback(self, read_time, read_value):
        print(self.mcu_adc.get_last_value())
        print(read_value)
        pass
    
    # def sample(self):
    #     print(self.mcu_adc.get_last_value())

    def __ready_event(self):
        # print(self.mcu_adc.get_last_value())
        pass

class Height_Handler:
    PATH_TO_PULSE_DATA = 'klippy/extras/thc_data'

    def __init__(self):
        pass

    def event(self):
        pass

    # def load_data(self):
    #     files = os.listdir(self.PATH_TO_PULSE_DATA)
    #     for file in files:
    #         key = '-'.join(file.split('.')[0].split('_')[-2::])
    #         with open(self.PATH_TO_PULSE_DATA + '/' + file, 'r') as f:
    #             reader = csv.reader(f)
    #             row = list(map(lambda x: (float(x) * 1e6).__ceil__(), next(reader)))
    #             self.__pulses_timings[key] = row

    

class Stepper_THC:
    PATH_TO_IMPULSE_TIMINGS = 'klippy/extras/thc_data/pulses_data.json'
    # _instance = None

    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super(Stepper_THC, cls).__new__(cls)
    #     return cls._instance
    

    # def __init__(self, pin_step, pin_dir, pin_enable, max_speed=1000, acceleration=100) -> None:
    def __init__(self, config) -> None:
        # super().__init__()
        self.__pulses_timings = {}
        self.load_data()
        # threading.Thread.__init__(self)
        # self.gpio = wpi.GPIO(1)
        self.pin_step = config.getint('sbp_pin_step')
        self.pin_dir = config.getint('sbp_pin_dir')
        self.pin_enable = config.getint('sbp_pin_en')
        # self.max_speed = config.getint('speed', 1000)  # steps per second
        # self.acceleration = config.getint('acceleration', 100)  # steps per second^2
        self.pulse_time = config.getfloat('step_pulse_duration', 0.000005)
        self.pulse_time_us = self.pulse_time * 10e6

        # Setup pins
        wpi.wiringPiSetup()
        wpi.pinMode(self.pin_step, GPIO.OUTPUT)
        wpi.pinMode(self.pin_dir, GPIO.OUTPUT)
        wpi.pinMode(self.pin_enable, GPIO.OUTPUT)
        # Set LOW all pins
        wpi.digitalWrite(self.pin_step, GPIO.LOW)
        wpi.digitalWrite(self.pin_dir, GPIO.LOW)
        wpi.digitalWrite(self.pin_enable, GPIO.HIGH)
        
        self.running = False
        self.target_steps = 0
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        # self.start()
    
    def load_data(self):
        with open(self.PATH_TO_IMPULSE_TIMINGS, 'r') as file:
            self.__pulses_timings = json.load(file)
            for i in self.__pulses_timings:
                if isinstance(self.__pulses_timings[i], (list, tuple)):
                    self.__pulses_timings[i] = list(map(lambda x: (x * 1e6).__ceil__(), self.__pulses_timings[i]))

    def blink_all_pins(self):
        """
        Needs for debug purpose, toogle pins
        """
        wpi.digitalWrite(self.pin_step, int(not wpi.digitalRead(self.pin_step)))
        wpi.digitalWrite(self.pin_dir, int(not wpi.digitalRead(self.pin_dir)))
        wpi.digitalWrite(self.pin_enable, int(not wpi.digitalRead(self.pin_enable)))

    def pulses_10_mm(self):
        for i in self.__pulses_timings['10-mm']:
            wpi.digitalWrite(self.pin_step, GPIO.HIGH)

    def set_direction(self, dir: int):
        wpi.digitalWrite(self.pin_dir, dir)

    def pin_toogle_low(self):
        wpi.digitalWrite(self.pin_step, wpi.LOW)

    def pin_toogle_high(self):
        wpi.digitalWrite(self.pin_step, wpi.HIGH)


    def trapezoidal_profile(self, steps):
        ramp_up_steps = self.max_speed ** 2 / (2 * self.acceleration)
        if steps < 2 * ramp_up_steps:
            ramp_up_steps = steps // 2
        ramp_down_steps = steps - ramp_up_steps
        
        time_step = 1 / self.max_speed
        for step in range(int(ramp_up_steps)):
            wpi.digitalWrite(self.pin_step, wpi.HIGH)
            time.sleep(time_step)
            wpi.digitalWrite(self.pin_step, wpi.LOW)
            time.sleep(time_step)
            time_step -= 1 / (2 * self.acceleration * (step + 1))

        time_step = 1 / self.max_speed
        for step in range(int(ramp_down_steps)):
            wpi.digitalWrite(self.pin_step, wpi.HIGH)
            time.sleep(time_step)
            wpi.digitalWrite(self.pin_step, wpi.LOW)
            time.sleep(time_step)
            time_step += 1 / (2 * self.acceleration * (step + 1))
    
    def run(self):
        while True:
            if self.running:
                pass
                # self.trapezoidal_profile(self.target_steps)
                for i in self.__pulses_timings['10-mm']:
                    # self.pulse_step()
                    start = wpi.micros()
                    wpi.digitalWrite(self.pin_step, GPIO.HIGH)
                    while wpi.micros() - start < 8:
                        pass
                    # sleep_microseconds(self.pulse_time_us)
                    # time.sleep(self.pulse_time)
                    # wpi.delayMicroseconds(10)
                    wpi.digitalWrite(self.pin_step, GPIO.LOW)
                    start = wpi.micros()
                    while wpi.micros() - start < i:
                        pass
                    # wpi.delayMicroseconds(250)
                self.running = False

    def move(self, steps, direction):
        self.target_steps = steps
        wpi.digitalWrite(self.pin_dir, direction)
        wpi.digitalWrite(self.pin_enable, GPIO.LOW)
        self.running = True

    def stop(self):
        self.running = False

    def _connect_event(self):
        try:
            
            print('Stepper THC connect event')
        except Exception as e:
            print(str(e))
            print('Stepper THC connect event failed!')
    
    def move_event(self):
        # while True:

        #     pass
        pass
    

    # def __del__(self):
    #     super(Stepper_THC, self).__del__()


class THC:

    def __init__(self, config) -> None:
        # Load objects from config
        self.printer = config.get_printer()
        self.__arc_pin = None
        self.__arc_pin_status = False
        self.__is_set_voltage = False
        self.voltage_value = 0.0
        self.buttons = self.printer.load_object(config, "buttons")
        self.gcode = self.printer.lookup_object('gcode')
        self.height_ctrl_stepper = Stepper_THC(config)
        self.adc = THC_ADC(config)

        # THC pins
        self.pin_up = config.get('pin_up')
        self.pin_down = config.get('pin_down')

        self.buttons.register_buttons([self.pin_up], self.button_up_callback)
        self.buttons.register_buttons([self.pin_down], self.button_down_callback)

        self.name = "THC"

        self._is_ready = False

        self.running = False
        self.reactor = self.printer.get_reactor()

        self.metall_sensor = self.printer.lookup_object('g_nome_metall_sensor')
        self.printer.register_event_handler("klippy:connect", self._connect_event)
        self.printer.register_event_handler("klippy:ready", self.__ready_event)
        self.printer.add_object("g_nome_thc", self)
        print('THC created')


    def __ready_event(self):
        self._is_ready = True
        pass 

    def check_arc_pin(self, eventtime):
        state = self.__arc_pin.get_status(eventtime)
        return bool(state['value'])

    def height_event(self, eventtime, state, direction):
        arc_pin_state = self.check_arc_pin(eventtime)
        if not state and arc_pin_state and self._is_ready:
                # self.height_ctrl_stepper.blink_all_pins()
                self.height_ctrl_stepper.move(100, direction)
                # self.height_ctrl_stepper.pulse_step()

        print('Button up callback: pin not ready!')

    def button_up_callback(self, eventtime, state):
        # self.height_ctrl_stepper.set_direction(1)
        self.height_event(eventtime=eventtime, state=state, direction=1)

    def button_down_callback(self, eventtime, state):
        # self.height_ctrl_stepper.set_direction(0)
        self.height_event(eventtime=eventtime, state=state, direction=0)

    def _connect_event(self):
        try:
            self.__arc_pin = self.printer.lookup_object('output_pin arc_on')
            # self.height_ctrl_stepper.blink_all_pins()
            print('THC connect event')
        except Exception as e:
            print(str(e))

def load_config(config):
    return THC(config)

def load_config_prefix(config):
    return THC(config)


if __name__ == "__main__":
    stepper_pin = 2
    dir_pin = 1
    enable_pin = 0
    stepper = Stepper_THC(0, 1)  # Adjust pin numbers as needed
    # stepper.start()
    stepper.move(1000, wpi.LOW)
    time.sleep(2)
    stepper.stop()
