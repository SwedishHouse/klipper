from typing import List
import re

class GCodeSplitter:

    MOVE_CMDS = ('G0', 'G00', 'G1', 'G01', 'G2', 'G02', 'G3', 'G03')

    def __init__(self) -> None:
        self.last_command = "G0"
        self.PATTERN = r'([GMSFTDH]-?\d+\.?\d*)|([XYZABCIJKR]-?\d+\.?\d*)|\(.*?\)'

    def __call__(self, *args, **kwds):
        
        return self.split_grouped_commands(*args)

    @staticmethod
    def replace_decimal_point(command):
        # Регулярное выражение для замены точки на нижнее подчеркивание в вещественных числах
        return re.sub(r'(\d+)\.(\d+)', r'\1_\2', command)

    @staticmethod
    def remove_comments(command):
        # Регулярное выражение для удаления комментариев внутри скобок
        return re.sub(r'\(.*?\)', '', command).strip()

    @staticmethod
    def has_multiple_commands(command):
        # Регулярное выражение для проверки наличия нескольких команд в строке
        pattern = r'^[GMSF]\d+(\.\d+)?(\s+[GMSF]\d+(\.\d+)?)+$'
        return re.match(pattern, command) is not None

    def is_coordinate_only(self, command):
        pattern = r'^[XYZABCIJ]\s*-?\d+(\.\d+)?(\s+[XYZABCIJ]\s*-?\d+(\.\d+)?)*$'
        return re.match(pattern, command) is not None

    def split_grouped_commands(self, commands):
        processed_commands = []
        for command in commands:
            command = self.remove_comments(command)
            # Проверка на наличие нескольких команд в строке
            if self.has_multiple_commands(command):
                # Разделение сгруппированных команд
                # split_commands = re.findall(r'[GMSF]\d+(\.\d+)?', command)
                split_commands = command.split()
                split_commands = [self.replace_decimal_point(cmd) for cmd in split_commands]
                processed_commands.extend(split_commands)
            elif self.is_coordinate_only(command):
                if self.last_command:
                    command = self.last_command + ' ' + command
                processed_commands.append(command)
            else:
                # command = self.replace_decimal_point(command)
                processed_commands.append(command)
                if len(command) > 0:
                    cmd_identifier = command.split()[0]
                    if cmd_identifier in self.MOVE_CMDS:
                        self.last_command = cmd_identifier
        return processed_commands

class PlasmaCodes:

    CODES = {'G21', 'G91_1', 'G00', 'G80', 'G01', 'G04', 'G40', 'M13', 'F', 'G54', 'G49', 'G02', 'M30', 'M15', 'G03', 'G90'}
    # CODES = {'G21', 'G91_1', 'G00', 'M05', 'G80', 'G01', 'G04', 'G40', 'M13', 'F', 'G54', 'G49', 'G02', 'M30', 'M03', 'M15', 'G03', 'G90'}

    PREFIX = 'cmd_'
    POSFIX_HELP = '_help'

    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.splitter = GCodeSplitter()
        setattr(self.gcode, 'available_multiple_plasma_codes', self.splitter)
        
        for i in self.CODES:
            try:
                self.gcode.register_command(i, getattr(self, self.PREFIX + i), \
                getattr(self, self.PREFIX + i + self.POSFIX_HELP))
            except Exception as e:
                print(str(e))

        self.printer.register_event_handler("klippy:connect", self._connect_event)
        self.printer.register_event_handler("klippy:ready", self.__ready_event)


    # def __extended_gcode_dispatch(self, gcmd):
    #     pass

    def _connect_event(self):
        pass

    def __ready_event(self):
        pass

    def __extendet_format_cmd(self, gcmd):
        cmd_num = int(gcmd.get('G', None))
        if not cmd_num:
            self.gcode.error('Not a integer value in gcode!')
        cmd_params = gcmd.get_raw_command_parameters()
        cmd = f'G{cmd_num} {cmd_params}'
        self.gcode.run_script_from_command(cmd)
        pass
    
    @staticmethod
    def parse_multiple_cmd(cmds: List[str]):
        pass

    cmd_G54_help = "Autogenerated help"
    def cmd_G54(self, gcmd):
        pass

    cmd_G02_help = "Autogenerated help"
    def cmd_G02(self, gcmd):
        self.__extendet_format_cmd(gcmd)

    cmd_G03_help = "Autogenerated help"
    def cmd_G03(self, gcmd):
        self.__extendet_format_cmd(gcmd)

    cmd_G90_help = "Autogenerated help"
    def cmd_G90(self, gcmd):
        pass

    cmd_G91_1_help = "Autogenerated help"
    def cmd_G91_1(self, gcmd):
        pass

    cmd_G49_help = "Autogenerated help"
    def cmd_G49(self, gcmd):
        pass

    cmd_G21_help = "Autogenerated help"
    def cmd_G21(self, gcmd):
        pass

    cmd_G04_help = "Autogenerated help"
    def cmd_G04(self, gcmd):
        self.__extendet_format_cmd(gcmd)

    cmd_F_help = "Autogenerated help"
    def cmd_F(self, gcmd):
        pass

    cmd_G80_help = "Autogenerated help"
    def cmd_G80(self, gcmd):
        pass

    cmd_M15_help = "Autogenerated help"
    def cmd_M15(self, gcmd):
        pass

    cmd_M05_help = "Autogenerated help"
    def cmd_M05(self, gcmd):
        pass

    cmd_G01_help = "Extendented G1 for CNC machine"
    def cmd_G01(self, gcmd):
        self.__extendet_format_cmd(gcmd)

    cmd_G40_help = "Autogenerated help"
    def cmd_G40(self, gcmd):
        pass

    cmd_G00_help = "Extendented G0 for CNC machine"
    def cmd_G00(self, gcmd):
        self.__extendet_format_cmd(gcmd)

    cmd_M30_help = "Autogenerated help"
    def cmd_M30(self, gcmd):
        pass

    cmd_M13_help = "Autogenerated help"
    def cmd_M13(self, gcmd):
        pass

    cmd_M03_help = "Autogenerated help"
    def cmd_M03(self, gcmd):
        pass


def load_config(config):
    return PlasmaCodes(config)

def load_config_prefix(config):
    return PlasmaCodes(config)

