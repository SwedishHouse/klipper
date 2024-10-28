import wiringpi as wpi
import threading
import time


class Stepper_THC:

    def __init__(self, pin_step, pin_dir, max_speed=1000, acceleration=100) -> None:
        threading.Thread.__init__(self)
        self.pin_step = pin_step
        self.pin_dir = pin_dir
        wpi.wiringPiSetupGpio()
        wpi.pinMode(self.pin_step, wpi.OUTPUT)
        wpi.pinMode(self.pin_dir, wpi.OUTPUT)
        self.running = False
        self.target_steps = 0
        self.max_speed = max_speed  # steps per second
        self.acceleration = acceleration  # steps per second^2
        pass


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
        while self.running:
            self.trapezoidal_profile(self.target_steps)
            self.running = False

    def move(self, steps, direction):
        self.target_steps = steps
        wpi.digitalWrite(self.pin_dir, direction)
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
        while True:

            pass


class THC:

    def __init__(self, config) -> None:
        self.printer = config.get_printer()
    
        self.__arc_pin = None
        # self.toolhead = None
        dir_pin, enable_pin = config.get('dir_pin'), config.get('enable_pin')
        pins = {'dir_pin':dir_pin, 'enable_pin': enable_pin}
        ppins = self.printer.lookup_object('pins')
        for key, val in pins.items():
            ppins.allow_multi_use_pin(val)
            setattr(self, key, ppins.setup_pin('digital_out', val))
        self.buttons = self.printer.load_object(config, "buttons")

        self.pwn_pin = config.get('pin_pwm')  # Like step
        self.cycle_time = config.getfloat('cycle_time', 0.01)
        self.max_power = config.getfloat('max_power', 1.0)
        self.pwm_pin = ppins.setup_pin('pwm', self.pwn_pin)
        self.pwm_pin.setup_cycle_time(self.cycle_time)
        self.pwm_pin.setup_max_duration(2)


        # THC pins
        self.pin_up = config.get('pin_up')
        self.pin_down = config.get('pin_down')

        self.buttons.register_buttons([self.pin_up], self.button_up_callback)
        self.buttons.register_buttons([self.pin_down], self.button_down_callback)

        self.name = "THC"
        self.gcode = self.printer.lookup_object('gcode')
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

    def set_pwm(self, value):
        self.pwm_pin.set_pwm(2, value)
    
    def set_dir_pin(self, value):
        self.dir_pin.set_digital(value)

    def set_enable_pin(self, value):
        self.enable_pin.set_digital(value)
    
    def button_up_callback(self, eventtime, state):

        if state and self._is_ready:
            try:

                self.set_pwm(0.5)
 
                pass
            except Exception as e:
                print(str(e))
        else:
            print('Pin not ready!')
            pass
        pass

    def button_down_callback(self, eventtime, state):
        
        if state and self._is_ready:
            try:
 
                
                
                pass
            except Exception as e:
                print(str(e))
        else:
            print('Pin not ready!')
            pass
        pass

    def _connect_event(self):
        try:
            self.__arc_pin = self.printer.lookup_object('output_pin arc_on')
            
            print('Yes')
        except Exception as e:
            print(str(e))

def load_config(config):
    return THC(config)

def load_config_prefix(config):
    return THC(config)


if __name__ == "__main__":
    stepper = Stepper_THC(0, 1)  # Adjust pin numbers as needed
    # stepper.start()
    stepper.move(1000, wpi.LOW)
    time.sleep(2)
    stepper.stop()