import time
from threading import Thread, Timer
'Event, Timer'
import math
from logic.config import GLOBAL_ADWIN_FPAR, SET_PAR_AND_F_PAR, CONTROL


class PIDControl(Thread):
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

        self.ts = 0.0125
        self.time_old = 0
        self.error = 0
        self.integral_error = 0
        self.derivative_error = 0
        self.error_last = 0
        self.u_output = 0
        self.duty_cycle = 0.050
        self.min_pid_output = 0
        self.max_pid_output = 10
        self.max_output = 10

        self.start()

    def stop_pid_control(self):
        self.active = False

    def run(self):
        while self.active:
            self.__pid_calc__()
            #time.sleep(0.0125)

    def __pid_calc__(self):
        self.hc = self.adw.Get_FPar(SET_PAR_AND_F_PAR['H_COM'])
        self.kp = self.adw.Get_FPar(SET_PAR_AND_F_PAR['P_GAIN'])
        self.ki = self.adw.Get_FPar(SET_PAR_AND_F_PAR['I_GAIN'])
        self.kd = self.adw.Get_FPar(SET_PAR_AND_F_PAR['D_GAIN'])
        self.kn = self.adw.Get_FPar(SET_PAR_AND_F_PAR['N_GAIN'])

        #self.ts = 1 / self.adw.Get_FPar(SET_PAR_AND_F_PAR['OMEGA_A'])
        self.pwm_time = self.adw.Get_FPar(GLOBAL_ADWIN_FPAR['TIME_CONTROL'])
        self.h_m = self.adw.Get_FPar(SET_PAR_AND_F_PAR['ALTITUDE'])
        #print(self.hc, self.kp, self.ki, self.kd, self.kn, self.ts)

        self.dt = self.pwm_time-self.time_old
        #self.ts = self.dt
        self.time_old = self.pwm_time

        self.error = self.hc - self.adw.Get_FPar(56)
        self.adw.Set_FPar(CONTROL['ERROR'], self.error)
        self.new_integral_error = self.integral_error + self.error * self.ts

        self.derivative_error = (self.error - self.error_last) / self.ts
        self.adw.Set_FPar(CONTROL['DERIVATIVE_ERROR'], self.derivative_error)

        self.control_u = self.kp * self.error + self.ki * self.new_integral_error + self.kd * self.derivative_error

        if self.control_u > self.max_pid_output:
            self.control_u = self.max_pid_output
            self.adw.Set_FPar(CONTROL['CONTROL_U'], self.control_u)
            self.new_integral_error = self.integral_error
            self.adw.Set_FPar(CONTROL['INTEGRAL_ERROR'], self.integral_error)
        elif self.control_u < self.min_pid_output:
            self.control_u = self.min_pid_output
            self.adw.Set_FPar(CONTROL['CONTROL_U'], self.control_u)
            self.new_integral_error = self.integral_error
            self.adw.Set_FPar(CONTROL['INTEGRAL_ERROR'], self.integral_error)
        else:
            self.control_u = self.control_u
            self.adw.Set_FPar(CONTROL['CONTROL_U'], self.control_u)
            self.integral_error = self.new_integral_error
            self.adw.Set_FPar(CONTROL['INTEGRAL_ERROR'], self.integral_error)

        #print(CONTROL['ERROR'], CONTROL['INTEGRAL_ERROR'], CONTROL['DERIVATIVE_ERROR'], CONTROL['CONTROL_U'])

        self.error_last = self.error
        self.__pwm__(self.control_u)

    def __pwm__(self, control_u):
        self.on_time = control_u / self.max_output * self.duty_cycle
        self.cycle_time = math.fmod(self.pwm_time, self.duty_cycle)
        if self.cycle_time < self.on_time:
            self.u_output = 1
        else:
            self.u_output = 0

        self.adw.Set_Par(CONTROL['ATV1'], self.u_output)
        #self.adw.Set_Par(CONTROL['ATV2'], self.u_output)
        print(control_u, self.pwm_time, self.u_output, self.on_time, self.cycle_time, self.dt)

