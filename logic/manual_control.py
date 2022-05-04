import time
from threading import Thread
from logic.config import SET_PAR_AND_F_PAR, CONTROL


class ManualControl(Thread):
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

        self.t_sample = 0.001
        self.atv1 = 0
        self.t_ein_atv1 = 0
        self.t_aus_atv1 = 0
        self.atv2 = 0
        self.t_ein_atv2 = 0
        self.t_aus_atv2 = 0

        self.start()

    def stop_manual_control(self):
        self.active = False

    def run(self):
        while self.active:
            self.__manual_calc__()
            time.sleep(self.t_sample)

    def __manual_calc__(self):
        self.atv1_on = self.adw.Get_Par(SET_PAR_AND_F_PAR["ATV1_ON"])
        self.pulse_time_on_atv1 = self.adw.Get_FPar(SET_PAR_AND_F_PAR["PULSE_ON_ATV1"])
        self.pulse_time_off_atv1 = self.adw.Get_FPar(SET_PAR_AND_F_PAR["PULSE_OFF_ATV1"])

        self.atv2_on = self.adw.Get_Par(SET_PAR_AND_F_PAR["ATV2_ON"])
        self.pulse_time_on_atv2 = self.adw.Get_FPar(SET_PAR_AND_F_PAR["PULSE_ON_ATV2"])
        self.pulse_time_off_atv2 = self.adw.Get_FPar(SET_PAR_AND_F_PAR["PULSE_OFF_ATV2"])

        # ATV1 :
        if self.atv1_on <= 0:
            if self.t_ein_atv1 == 0:
                self.atv1 = 0
                self.t_ein_atv1 = 0
                self.t_aus_atv1 = self.t_aus_atv1 + self.t_sample
            else:
                if self.t_ein_atv1 < self.pulse_time_on_atv1:
                    self.atv1 = 1
                    self.t_ein_atv1 = self.t_ein_atv1 + self.t_sample
                    self.t_aus_atv1 = 0
                else:
                    self.atv1 = 0
                    self.t_ein_atv1 = 0
                    self.t_aus_atv1 = self.t_aus_atv1 + self.t_sample
        else:
            if self.t_ein_atv1 < self.pulse_time_on_atv1:
                if self.t_aus_atv1 == 0:
                    self.atv1 = 1
                    self.t_ein_atv1 = self.t_ein_atv1 + self.t_sample
                    self.t_aus_atv1 = 0
                else:
                    if self.t_aus_atv1 < self.pulse_time_off_atv1:
                        self.atv1 = 0
                        self.t_ein_atv1 = 0
                        self.t_aus_atv1 = self.t_aus_atv1 + self.t_sample
                    else:
                        self.atv1 = 1
                        self.t_ein_atv1 = self.t_ein_atv1 + self.t_sample
                        self.t_aus_atv1 = 0
            else:
                self.atv1 = 0
                self.t_ein_atv1 = 0
                self.t_aus_atv1 = self.t_aus_atv1 + self.t_sample

        # ATV2 :
        if self.atv2_on <= 0:
            if self.t_ein_atv2 == 0:
                self.atv2 = 0
                self.t_ein_atv2 = 0
                self.t_aus_atv2 = self.t_aus_atv2 + self.t_sample
            else:
                if self.t_ein_atv2 < self.pulse_time_on_atv2:
                    self.atv2 = 1
                    self.t_ein_atv2 = self.t_ein_atv2 + self.t_sample
                    self.t_aus_atv2 = 0
                else:
                    self.atv2 = 0
                    self.t_ein_atv2 = 0
                    self.t_aus_atv2 = self.t_aus_atv2 + self.t_sample
        else:
            if self.t_ein_atv2 < self.pulse_time_on_atv2:
                if self.t_aus_atv2 == 0:
                    self.atv2 = 1
                    self.t_ein_atv2 = self.t_ein_atv2 + self.t_sample
                    self.t_aus_atv2 = 0
                else:
                    if self.t_aus_atv2 < self.pulse_time_off_atv2:
                        self.atv2 = 0
                        self.t_ein_atv2 = 0
                        self.t_aus_atv2 = self.t_aus_atv2 + self.t_sample
                    else:
                        self.atv2 = 1
                        self.t_ein_atv2 = self.t_ein_atv2 + self.t_sample
                        self.t_aus_atv2 = 0
            else:
                self.atv2 = 0
                self.t_ein_atv2 = 0
                self.t_aus_atv2 = self.t_aus_atv2 + self.t_sample

        self.adw.Set_Par(CONTROL['ATV1'], self.atv1)
        print('atv1', self.atv1)
        self.adw.Set_Par(CONTROL['ATV2'], self.atv2)
        #print('atv2', self.atv2)
