import time
from threading import Thread
import cmath
from logic.config import GLOBAL_ADWIN_FPAR, SET_PAR_AND_F_PAR, CONTROL


class SuicideBurn(Thread):
    """
  Timer that runs in new thread and calls a callback fn infinitely, with a minimum
  temporal delta of MIN_PERIOD_MS
  """
    MIN_PERIOD_MS = 1
    SLEEP_FACTOR = 1

    def __init__(self, adw) -> None:
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.adw = adw

        self.mass = 2.7
        self.g = 9.806
        self.thrust = 35
        #self.pressure = self.adw.Get_FPar(GLOBAL_ADWIN_FPAR['PRESSURE'])
        #self.thrust = self.pressure
        #print('p', self.pressure)
        self.error = 0

        self.actuator_time_start = self.adw.Get_FPar(GLOBAL_ADWIN_FPAR['TIME_CONTROL'])
        self.hc = self.adw.Get_FPar(SET_PAR_AND_F_PAR['H_COM'])
        self.h0 = self.adw.Get_FPar(SET_PAR_AND_F_PAR['H_0'])
        #print('h0', self.h0, 'hc', self.hc)
        self.acc = self.g - self.thrust / self.mass
        self.t_burn_start = cmath.sqrt((2 * (self.hc - self.h0) * self.acc) / (self.g * (self.g - self.acc)))
        self.t_burn_start = self.t_burn_start.real
        self.adw.Set_FPar(CONTROL['TIMETOBURN'], self.t_burn_start)
        self.v_burn_start = self.g * self.t_burn_start
        self.h_burn_start = self.h0 - self.g / 2 * self.t_burn_start ** 2
        self.burn_time = (cmath.sqrt(self.v_burn_start ** 2 - 2 * self.acc * (self.hc - self.h0)) - self.v_burn_start) / self.acc
        self.burn_time = self.burn_time.real
        self.t_end = self.t_burn_start + self.burn_time
        self.adw.Set_FPar(CONTROL['BURNTIME'], self.burn_time)
        self.burn_altitude = self.h0 - self.g / 2 * self.t_burn_start ** 2
        self.adw.Set_FPar(CONTROL['BURNALTITUDE'], self.burn_altitude)
        #print('time', self.actuator_time_start, 'timetoburn', self.t_burn_start, 'burn_time', self.burn_time, 'alti', self.burn_altitude)

        self.start()

    def stop_suicide_burn(self):
        self.active = False

    def run(self):
        while self.active:
            self.__suicide_calc__()
            #time.sleep(0.0005)

    def __suicide_calc__(self):
        self.actuator_time_current = self.adw.Get_FPar(GLOBAL_ADWIN_FPAR['TIME_CONTROL'])
        self.dt = self.actuator_time_current - self.actuator_time_start
        if self.dt < self.t_end:
            if self.dt < self.t_burn_start:
                self.valve_com = 0
            else:
                self.valve_com = 1
        else:
            self.valve_com = 0

        #print('dt', self.dt, 'value', self.valve_com)
        self.adw.Set_Par(CONTROL['ATV1'], self.valve_com)


