


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

    cmd_GET_RAW_THC_ADC_VALUE_help = "Get raw value from THC ADC"
    cmd_GET_THC_ADC_VALUE_help = "Get voltage value from THC ADC"

    cmd_GET_RAW_THC_ADC_VALUE_str = "GET_RAW_THC_ADC_VALUE"
    cmd_GET_THC_ADC_VALUE_str = "GET_THC_ADC_VALUE"


    def __init__(self, config) -> None:
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        ppins = self.printer.lookup_object('pins')
        pin_name = config.get('sensor_pin', "PA6")
        self.pin = pin_name
        self.mcu_adc = ppins.setup_pin('adc', pin_name)
        self.mcu_adc.setup_adc_callback(REPORT_TIME, self.callback)
        self.mcu_adc.setup_adc_sample(SAMPLE_TIME, SAMPLE_COUNT)

        self.__voltage = config.getfloat('vref_voltage', 3.3)
        self.value = 0.0
        self.status = {'raw':0.0, 'voltage': 0.0}
        self.gcode.register_command(self.cmd_GET_RAW_THC_ADC_VALUE_str, self.cmd_GET_RAW_THC_ADC_VALUE, desc=self.cmd_GET_RAW_THC_ADC_VALUE_help)
        self.gcode.register_command(self.cmd_GET_THC_ADC_VALUE_str, self.cmd_GET_THC_ADC_VALUE, desc=self.cmd_GET_THC_ADC_VALUE_help)
        self.gcode.register_command('QUERY_THC_ADC', self.cmd_QUERY_THC_ADC)
        self.printer.register_event_handler("klippy:ready", self.__ready_event)
        pass

    def cmd_GET_RAW_THC_ADC_VALUE(self, gcmd):
        return self.status

    def cmd_GET_THC_ADC_VALUE(self, gcmd):
        return self.status['voltage']
    
    def cmd_QUERY_THC_ADC(self, params):
        self.gcode.respond_info(f"THC_ADC on {self.pin}: {self.status}")

    def callback(self, read_time, read_value):
        self.value = self.mcu_adc.get_last_value()[0]
        self.status['raw'] = self.value
        self.status['voltage'] = self.value * self.__voltage
        # print(self.mcu_adc.get_last_value())
        # print(read_value)
        # pass
    
    # def sample(self):
    #     print(self.mcu_adc.get_last_value())

    def __ready_event(self):
        # print(self.mcu_adc.get_last_value())
        pass

def load_config(config):
    return THC_ADC(config)

def load_config_prefix(config):
    return THC_ADC(config)