# Support for i2c based temperature sensors
#
# Copyright (C) 2023  Vadim Mescheryakov swedish2015@yandex.ru
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
from . import bus

I2C_ADDRESSES = {'GROUND': 0b1001000, 'VDD': 0b1001001, 'SDA': 0b1001010, 'SCL':0b1001011}
channels = 0, 1, 2, 3
params_list = 'i2c_address',
REPORT_TIME = .8

class ADS1115:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.reactor = self.printer.get_reactor()
        address = config.getint('i2c_address')
        if address not in I2C_ADDRESSES.values():
            raise TypeError(f"Your address must be in {str(list(I2C_ADDRESSES.values()))}, but get {address}")
        self.__address = address
        channel = config.getint('channel')
        if channel not in channels:
            raise TypeError(f"Your channel must be in {str(channels)}, but get {channel}")
        self.__channel = channel
        # raise TypeError('Vadim be honest with yourself. You don\'t know how to write this driver')
        self.i2c = bus.MCU_I2C_from_config(
            config, default_addr=self.__address, default_speed=100000)
    
    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp
    
    def setup_callback(self, cb):
        self._callback = cb

    def read_register(self, reg_name, read_len):
        # read a single register
        regs = [self.chip_registers[reg_name]]
        params = self.i2c.i2c_read(regs, read_len)
        return bytearray(params['response'])


    def get_report_time_delta(self): # @todo needs to change in corresponding with datasheet
        return REPORT_TIME

    def write_register(self, reg_name, data):
        if type(data) is not list:
            data = [data]
        reg = self.chip_registers[reg_name]
        data.insert(0, reg)
        self.i2c.i2c_write(data)

def load_config(config):
    # Register sensor
    pheaters = config.get_printer().load_object(config, "heaters")
    pheaters.add_sensor_factory("ads1115", ADS1115)
