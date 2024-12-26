import abc
import threading

class Signal(metaclass=abc.ABCMeta):

   """
   Abstract base class for signals.

   Signals is an abstract base class that defines the interface for signals. It provides three abstract methods: connect, disconnect, and emit.

   Methods:
   - connect(slot): Connects a slot to the signal.
   - disconnect(slot): Disconnects a slot from the signal.
   - emit(*args, **kwargs): Emits the signal with the given arguments.
   """

   @abc.abstractmethod
   def connect(self, slot):
       """
       Connects a slot to the signal.

       Args:
           slot: The slot to be connected to the signal.

       Returns:
           None
       """
       pass

   @abc.abstractmethod
   def disconnect(self, slot):
       """
       Disconnects a slot from the signal.

       Args:
           slot: The slot to be disconnected from the signal.

       Returns:
           None
       """
       pass

   @abc.abstractmethod 
   def emit(self, *args, **kwargs) -> None:
       """
       Emits the signal with the given arguments.

       Args:
           *args: Variable length argument list.
           **kwargs: Arbitrary keyword arguments.

       Returns:
           None
       """
       pass

class MetalSensor(Signal):

    sensor_types = {'NPN': 1, 'PNP': 1}
    send = {'time': 0.0, 'state': False}

    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        # self.name = config.get_name().split(' ')[-1]
        # Object params
        self.__is_ready = False
        self.__last_button_event_time = 0.0 # Needs for handling contact bounce
        self.__button_event_is_set = False
        self.sensor_event_handler = None # Needs for Metal table event handling
        self.last_state = 0

        # Some params read from config

        self.sensor_type = config.get('sensor_type', 'NPN')
        if self.sensor_type not in self.sensor_types:
            raise ValueError(f'Unknown sensor type {self.sensor_type}')
        else:
            self.active_state = self.sensor_types[self.sensor_type]
    
        self.pin = config.get('pin')
        
        # Set up button for handling metal sensor events
        buttons = self.printer.load_object(config, "buttons")
        if config.get('analog_range', None) is None:
            buttons.register_buttons([self.pin], self.button_callback)
        else:
            amin, amax = config.getfloatlist('analog_range', count=2)
            pullup = config.getfloat('analog_pullup_resistor', 4700., above=0.)
            buttons.register_adc_button(self.pin, amin, amax, pullup,
                                        self.button_callback)
        
        self.printer.register_event_handler("klippy:ready", self.__ready_event) # When will be ready we can start reading the sensor
        self.printer.add_object("g_nome_metall_sensor", self) # Save the object for later use
    
    def connect(self, slot):
        if not self.sensor_event_handler:
            self.sensor_event_handler = slot
    
    def disconnect(self, slot=None):
        self.sensor_event_handler = slot

    def emit(self, *args, **kwargs) -> None:
        if self.sensor_event_handler:
            self.sensor_event_handler(*args, **kwargs)

    def __ready_event(self):
        self._is_ready = True

    def button_callback(self, eventtime, state):
        # if not self.__button_event_is_set:
        #     self.__button_event_is_set = True
        #     self.__last_button_event_time = eventtime
        if self.__is_ready and self.__is_activated(state):
            self.emit(eventtime, True)
    
    def start(self):
        self.__is_ready = True
    
    def __is_activated(self, state):
        return self.active_state == state
    
    def setup_event_hanler(self, event_hanler):
        self.sensor_event_handler = event_hanler
 
class MachineTableSheetFinder:

    cmd_FIND_METAL_SHEET_str = 'FIND_METAL_SHEET'
    cmd_FIND_METAL_SHEET_help = "The beginning of the metal sheet search process"


    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        self.config = config
        self.__limit = None
        self.__startSearchPoint = config.getfloat('start_height', 50.0)
        self.__speed = config.getfloat('feedrate', 2000.0)
        self.__sheetThickness = config.getfloat('sheet_thickness', 3.0)
        self.__cutterDistanceToSheet = config.getfloat('work_height', 3.0)
        self.__step_distances = (3.0, 1.0, 0.5, 0.25, 0.1)
        self.__step_distance = config.getfloat('step_distance', 1.0)
        self.__is_run = False
        self.__sensor_state = {'time': 0.0, 'state': False}
        self.__axis_max = None

        self.sensor:MetalSensor = MetalSensor(self.config)
        self.gcode = self.printer.lookup_object('gcode')
        self.toolhead = None
        self.gcode.register_command(self.cmd_FIND_METAL_SHEET_str, self.cmd_FIND_METAL_SHEET, desc=self.cmd_FIND_METAL_SHEET_help)
        self.printer.register_event_handler("klippy:connect", self._connect_event)
        self.printer.register_event_handler("klippy:ready", self._ready_event)

    @property
    def get_sheet_thickness(self):
        return self.__sheetThickness
    
    @get_sheet_thickness.setter
    def get_sheet_thickness(self, value):
        self.__sheetThickness = value
        

    def go_to_start_position(self):
        self.gcode.run_script_from_command(f"G90\nG0 Z{self.__startSearchPoint}")
        pass

    def sensor_event(self, time, state):
        self.__sensor_state['time'] = time
        self.__sensor_state['state'] = state
        
    def __calc_start_position(self):
        if self.__startSearchPoint >= self.__limit:
            self.__startSearchPoint = self.__limit * 0.9
        
    def _connect_event(self):# Called when the printer is connected
        self.toolhead = self.printer.lookup_object('toolhead')
        self.__limit = self.toolhead.kin.axes_max.z
        self.sensor.connect(self.sensor_event)
        pass

    def move_down_and_check_touch(self):
        current_speed = self.toolhead
        while not self.__sensor_state['state']:
            
            self.gcode.run_script_from_command("G91\n"
                                                f"G0 Z-{self.__step_distance}F{self.__speed}\n"
                                                "G90")
            self.toolhead.wait_moves()
        self.gcode.run_script_from_command("G91\n"
                                                f"G0 Z-{self.__sheetThickness + self.__cutterDistanceToSheet}\n"
                                                "G90")

    def _ready_event(self):
        pass
        # self.sensor.connect()

    def cmd_FIND_METAL_SHEET(self, gcmd):
        pass
        self.__is_run = True
        self.__calc_start_position()
        self.sensor.start()
        self.go_to_start_position()
        try:
            self.move_down_and_check_touch()
        except Exception as e:
            raise gcmd.error('No metal sheet!')
        self.__is_run = False
        self.__sensor_state['state'] = False


        pass


def load_config(config):
    return MachineTableSheetFinder(config)

def load_config_prefix(config):
    return MachineTableSheetFinder(config)