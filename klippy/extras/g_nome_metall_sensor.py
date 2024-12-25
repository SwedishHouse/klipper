# Support for metall sensor for Plasma cutter
#
#
#

class MetalSensor:

    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        self.name = config.get_name().split(' ')[-1]
        self.pin = config.get('pin')
        self.last_state = 0
        buttons = self.printer.load_object(config, "buttons")
        if config.get('analog_range', None) is None:
            buttons.register_buttons([self.pin], self.button_callback)
        else:
            amin, amax = config.getfloatlist('analog_range', count=2)
            pullup = config.getfloat('analog_pullup_resistor', 4700., above=0.)
            buttons.register_adc_button(self.pin, amin, amax, pullup,
                                        self.button_callback)
            
        self.printer.add_object("g_nome_metall_sensor", self)
            
        
        print('G-NOME CODE!')

    def button_callback(self, eventtime, state):
        print(f'Metall Callback {state}')

def load_config(config):
    return MetalSensor(config)

def load_config_prefix(config):
    return MetalSensor(config)

