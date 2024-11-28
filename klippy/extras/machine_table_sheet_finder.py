import abc


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

    sensor_types = {'NPN': 0, 'PNP': 1}

    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        self.name = config.get_name().split(' ')[-1]
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
        if not self.__button_event_is_set:
            self.__button_event_is_set = True
            self.__last_button_event_time = eventtime
    
    def __is_activated(self, state):
        return self.active_state == state
    
    def setup_event_hanler(self, event_hanler):
        self.sensor_event_handler = event_hanler
 

def load_config(config):
    return MetalSensor(config)

def load_config_prefix(config):
    return MetalSensor(config)