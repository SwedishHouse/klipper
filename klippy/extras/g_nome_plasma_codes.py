from typing import List
import re

class GCodeSplitter:

    MOVE_CMDS = ('G0', 'G00', 'G1', 'G01', 'G2', 'G02', 'G3', 'G03')

    def __init__(self) -> None:
        self.last_cmd = None
        self.PATTERN = r'([GMSFTDH]-?\d+\.?\d*)|([XYZIJKR]-?\d+\.?\d*)|\(.*?\)'

    @staticmethod
    def is_coordinate_command(command):
        # Регулярное выражение для проверки, содержит ли команда только координаты
        pattern = r"\b(?:[XYZABC](?:\+|-)?\d+(?:\.\d+)?)|[IJKP](?:\+|-)?\d+(?:\.\d+)?\b"
        return re.match(pattern, command) is not None

    def modify_coord_cmds(self, cmds):
        last_command = None  # Переменная для хранения последнего идентификатора команды
    
        result = []
        
        for command_str in cmds:
            # Проверяем, является ли текущая строка командой
            if not self.is_coordinate_command(command_str):
                sub_cmd = command_str.split()
                if len(sub_cmd) > 0:
                    last_command = sub_cmd[0]  # Сохраняем последнюю команду
                result.append(command_str)
            else:
                # Если строка состоит только из координат, добавляем к ней последний известный идентификатор команды
                if last_command is not None:
                    result.append(last_command + ' ' + command_str.strip())
                else:
                    raise ValueError("Не найдена ни одной команды до координат.")
                    
        return result

    def parse_gcode_line(self, line: list) -> list:
        # Регулярное выражение для поиска команд и их параметров
        result = []
        for item in line:
            matches = re.findall(self.PATTERN, item)

            # Объединяем команды и параметры в один список
            commands = []
            current_command = None

            for match in matches:
                command = match[0] if match[0] else match[1]
                if re.match(r'^[GMS][0-9]+(\.[0-9]+)?$', command):
                    command = command.replace('.', '_')
                # Если это новая команда, добавляем ее в список
                if re.match(r'[GMSFTDH]', command):
                    if current_command:
                        commands.append(current_command)
                    current_command = command
                    if command in self.MOVE_CMDS:
                        self.last_cmd = command
                else:
                    # Если это параметр, добавляем его к текущей команде
                    if current_command:
                        current_command += ' ' + command

            # Добавляем последнюю команду
            if current_command:
                commands.append(current_command.strip())

            result.extend(commands)
            if result:
                self.last_cmd = result[0]
        return result

class PlasmaCodes:

    CODES = {'G21', 'G91_1', 'G00', 'M05', 'G80', 'G01', 'G04', 'G40', 'M13', 'F', 'G54', 'G49', 'G02', 'M30', 'M03', 'M15', 'G03', 'G90'}
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
        pass

    cmd_G03_help = "Autogenerated help"
    def cmd_G03(self, gcmd):
        pass

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
        pass

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

