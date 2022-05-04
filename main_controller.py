import sys
from PyQt5 import QtWidgets
from logic.timer import Timer
from adwin.ADwin import ADwin
from logic.event_handler import EventHandler
from qt_ui.lander_ui import LanderUI


class M11Lander:
    DEVICENUMBER = 0x1

    def __init__(self) -> None:
        self.adw = ADwin(M11Lander.DEVICENUMBER, 1)
        self.qt_app = QtWidgets.QApplication(sys.argv)
        self.event_handler = EventHandler(self.adw, self.restart_timer)
        self.window = LanderUI(self.event_handler)
        self.window.show()
        self.timer = None
        # exit process when window closes
        sys.exit(self.qt_app.exec_())

    def restart_timer(self):
        if self.timer and self.timer.is_alive():
            self.timer.stop_timer()
        self.timer = Timer(self.on_timer_event)

    def on_timer_event(self):
        self.event_handler.on_timer_event(self.window, self.qt_app.processEvents)



if __name__ == '__main__':
    M11Lander()
