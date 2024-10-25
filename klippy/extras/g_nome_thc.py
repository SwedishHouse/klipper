import threading
import time


class Stepper_THC:

    def __init__(self, config) -> None:
        # self.printer = config.get_printer()
        # self.reactor = self.printer.get_reactor()
        # self.mcu = self.printer.lookup_object('mcu')
        # self.running = False
        # step_pin, dir_pin, enable_pin = config.get("step_pin"), config.get("dir_pin"), config.get("enable_pin")
        # pins = {'step_pin':step_pin, 'dir_pin':dir_pin, 'enable_pin':enable_pin}
        # ppins = self.printer.lookup_object('pins')
        # for key, val in pins.items():
        #     ppins.allow_multi_use_pin(val)
        #     setattr(self, key, ppins.setup_pin('digital_out', val))
        #     # self.step_pin = ppins.setup_pin('digital_out', val)
        # # self.dir_pin = None
        # # self.en_pin = None
        # self.printer.register_event_handler("klippy:connect", self._connect_event)
        # self.__pin_steps = 1000
        # self.printer.add_object("stepper_thc", self)
        pass

    def _connect_event(self):
        try:
            # z_stepper = self.printer.lookup_object('toolhead')
            # threading.Thread(target=self.move_event).start()
            print('Z found!')
        except Exception as e:
            print(str(e))
            print('No Z stepper')
    
    def move_event(self):
        while True:
            # if self.running:
            #     self.enable_pin.set_digital(1,1)
            #     for i in range(self.__pin_steps):
            #         self.step_pin.set_digital(1,1)
            #         time.sleep(0.001)
            #         self.step_pin.set_digital(1,0)
            #     self.running = False
            pass


class THC:

    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        # self.manual_stepper = None
        self.__arc_pin = None
        # self.toolhead = None
        dir_pin, enable_pin = config.get('dir_pin'), config.get('enable_pin')
        pins = {'dir_pin':dir_pin, 'enable_pin': enable_pin}
        ppins = self.printer.lookup_object('pins')
        for key, val in pins.items():
            ppins.allow_multi_use_pin(val)
            setattr(self, key, ppins.setup_pin('digital_out', val))
        self.buttons = self.printer.load_object(config, "buttons")
        # Stepper pins
        # Step 
        self.pwn_pin = config.get('pin_pwm')  # Like step
        self.cycle_time = config.getfloat('cycle_time', 0.01)
        self.max_power = config.getfloat('max_power', 1.0)
        self.pwm_pin = ppins.setup_pin('pwm', self.pwn_pin)
        self.pwm_pin.setup_cycle_time(self.cycle_time)
        self.pwm_pin.setup_max_duration(2)
        # self.pwm_pin.setup_pwm(self.cycle_time, self.max_power)

        # Direction
        # self.dir_pin = config.get('dir_pin') 
        # self.dir_pin = self.printer.lookup_pin(self.dir_pin)
        # # self.dir_pin.setup_pin('digital_out')
        # # Enable pin
        # self.enable_pin = config.get('enable_pin') 
        # self.enable_pin = self.printer.lookup_pin(self.enable_pin)

        # THC pins
        self.pin_up = config.get('pin_up')
        self.pin_down = config.get('pin_down')

        self.buttons.register_buttons([self.pin_up], self.button_up_callback)
        self.buttons.register_buttons([self.pin_down], self.button_down_callback)
        # self.stepper_thc = Stepper_THC(config)
        self.name = "THC"
        self.gcode = self.printer.lookup_object('gcode')
        self._is_ready = False
        # self.gcode.register_command("M3", self.cmd_M3,
        #                                 desc=self.cmd_M3_help)
        # self.mcu = config.get('mcu')
        # self.steppers = self.mcu.get('steppers')
        
        self.running = False
        self.reactor = self.printer.get_reactor()
        # buttons = self.printer.load_object(config, "buttons")
        # buttons.register_buttons([self.pin_up], self.button_up_callback)
        # buttons.register_buttons([self.pin_down], self.button_down_callback)
        self.metall_sensor = self.printer.lookup_object('g_nome_metall_sensor')
        self.printer.register_event_handler("klippy:connect", self._connect_event)
        self.printer.register_event_handler("klippy:ready", self.__ready_event)
        self.printer.add_object("g_nome_thc", self)
        print('THC created')

    # cmd_M3_help = "Turn on Plasma Cutter"

    # def cmd_M3(self):
    #     print('M3 execute')

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
        # try:
        #     if self.toolhead is not None and not state:
        #         current_position = self.toolhead.get_position()
        #         self.toolhead.manual_move([None, None, current_position[2]+10], self.toolhead.get_max_velocity()[0])
        #         self.reactor.pause(0.1)
        # except Exception as e:
        #     print(str(e))
        if state and self._is_ready:
            try:
                # self.set_enable_pin(1)
                # self.set_dir_pin(1)
                self.set_pwm(0.5)
                # position = self.toolhead.get_position()[0]
                # print(position)
                # print(self.manual_stepper.get_position())
                # self.manual_stepper.do_set_position(0)
                # self.manual_stepper.do_enable(0)
                # print(f'Pressed UP at {position}')
                # self.stepper_thc.running = True
                # self.gcode.run_script_from_command('M400')
                # self.gcode.run_script_from_command(f"MANUAL_STEPPER STEPPER=thc_stepper ENABLE=0 SET_POSITION=0 MOVE={-10} SYNC=0")
                # self.manual_stepper.flush_step_generation()
                # self.manual_stepper.do_move(position - 10, 50, 200, False)
                
                pass
            except Exception as e:
                print(str(e))
        else:
            print('Pin not ready!')
            pass
        pass

    def button_down_callback(self, eventtime, state):
        # try:
        #     if self.toolhead is not None and not state:
        #         current_position = self.toolhead.get_position()
        #         self.toolhead.manual_move([None, None, current_position[2]-10], self.toolhead.get_max_velocity()[0])
        #         self.reactor.pause(0.1)
        # except Exception as e:
        #     print(str(e))
        # if state and self._is_ready and self.__arc_pin.get_status(self.reactor.NOW):
        if state and self._is_ready:
            try:
                # self.set_enable_pin(0)
                # self.set_dir_pin(0)
                self.set_pwm(0.5)
                # position = self.toolhead.get_position()[0]
                # print(position)
                # print(self.manual_stepper.get_position())
                # self.manual_stepper.do_set_position(0)
                # self.manual_stepper.do_enable(0)
                # print(f'Pressed Down at {position}')
                # self.stepper_thc.running = True
                # self.gcode.run_script_from_command('M400')
                # self.gcode.run_script_from_command(f"MANUAL_STEPPER STEPPER=thc_stepper MOVE=10 SET_POSITION=0 SPEED=50 SYNC=0")
                # self.manual_stepper.flush_step_generation()
                # self.manual_stepper.do_move(position + 10, 50, 200, False)
                
                pass
            except Exception as e:
                print(str(e))
        else:
            print('Pin not ready!')
            pass
        pass

    def _connect_event(self):
        try:
            # self.toolhead = self.printer.lookup_object('toolhead')
            # self.toolhead = self.printer.lookup_object('stepper_z')
            # self.toolhead.manual_move([None, None, 10], self.toolhead.get_max_velocity())
            # self.manual_stepper = self.printer.lookup_object('manual_stepper thc_stepper')
            self.__arc_pin = self.printer.lookup_object('output_pin arc_on')
            
            print('Yes')
        except Exception as e:
            print(str(e))

def load_config(config):
    return THC(config)

def load_config_prefix(config):
    return THC(config)