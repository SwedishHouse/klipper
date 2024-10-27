# motion_queue.py
import logging
# from klippy import klippy

def load_config(config):
    return MotionQueue(config)

class MotionQueue:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.toolhead = None
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command('QUEUE_MOVE', self.cmd_queue_move)
        self.gcode.register_command('CLEAR_QUEUE', self.cmd_clear_queue)
        self.printer.register_event_handler("klippy:connect", self._connect_event)
        self.printer.add_object("motion_queue", self)
        
    def _connect_event(self):
        self.toolhead = self.printer.lookup_object('toolhead')
        
    def cmd_queue_move(self, params):
        move = {
            "position": params.get("Z", 0),
            "velocity": params.get("F", 0)
        }
        logging.info(f"Adding move: {move}")
        # self.toolhead.move_to(move["position"], move["velocity"])
        self.toolhead.drip_move(move["position"], move["velocity"], None)

    def cmd_clear_queue(self, params):
        logging.info("Clearing queue")
        # self.toolhead.dwell(0)  # This effectively clears the move queue
        
        # self.toolhead.flush_moves()
