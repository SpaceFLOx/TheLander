from logic.datavalues import DataValues
from qt_ui.lander_ui import LanderUI, UIInputValue
from logic.pid_control import PIDControl
from logic.suicide_burn import SuicideBurn
from logic.config import *
import os
import numpy as np
import time

BTL = "ADwin11.btl"  # taken from C:\


class EventHandler:

    def __init__(self, adw, restart_timer):
        self.adw = adw
        self.boot_load_adwin = self.adw.ADwindir + BTL
        self.data_values = DataValues(self.adw)
        self.restart_timer = restart_timer
        self.manual_control = None
        self.pid_control = None
        self.suicide_burn = None

    def on_boot(self):
        self.adw.Boot(self.boot_load_adwin)
        self.__load_all_processes()
        self.__clear_all_par()
        self.__start_all_sensor_processes()

    def __load_all_processes(self):
        for process_name in PROCESS_PATHS.values():
            self.adw.Load_Process(process_name)

    def __clear_all_par(self):
        for global_adw_index in range(0, 80):  # 80 global integer parameters available
            self.adw.Set_Par(global_adw_index + 1, 0)  # ADwin is 1 based
            self.adw.Set_FPar(global_adw_index + 1, 0)  # ADwin is 1 based

    def __start_all_sensor_processes(self):
        for process_number in SENSOR_PROCESS_IDS:
            self.adw.Start_Process(process_number)
        self.restart_timer()

    def on_start(self):
        self.__start_all_processes()
        self.clear_fifo()

    def __start_all_processes(self):
        for process_number in PROCESS_PATHS.keys():
            self.adw.Start_Process(process_number)

    def clear_fifo(self):
        self.__clear_fifo_array()

    def __clear_fifo_array(self):
        for fifo in ALL_FIFO.values():
            self.adw.Fifo_Clear(fifo)

    def on_quit(self, test_id):
        self.on_stop(test_id)
        self.__stop_all_processes()
        self.__clear_all_processes()

    def __stop_all_processes(self):
        for process_number in PROCESS_PATHS.keys():
            self.adw.Stop_Process(process_number)

    def __clear_all_processes(self):
        for process_number in PROCESS_PATHS.keys():
            self.adw.Clear_Process(process_number)

    def on_stop(self, test_id):
        while any(self.adw.Get_Par(i) != 0 for i in ACTUATOR_NAME_TO_ADWIN_PAR.values()):
            for ADWIN_PAR in ACTUATOR_NAME_TO_ADWIN_PAR.values():
                self.adw.Set_Par(ADWIN_PAR, 0)
                time.sleep(0.1)
        self.__stop_all_non_sensor_processes()
        if test_id != "":
            self.on_save(test_id)

    def __stop_all_non_sensor_processes(self):
        for process_number in NON_SENSOR_PROCESS_IDS:
            self.adw.Stop_Process(process_number)

    def on_sequence(self):
        self.adw.Set_Par(SET_PAR_AND_F_PAR["SEQUENCE_ON"], 1)

    def off_sequence(self):
        self.adw.Set_Par(SET_PAR_AND_F_PAR["SEQUENCE_ON"], 0)

    def on_pid(self):
        self.pid_control = PIDControl(self.adw)
        self.adw.Set_Par(SET_PAR_AND_F_PAR["PID_ON"], 1)

    def off_pid(self):
        self.pid_control.stop_pid_control()
        self.adw.Set_Par(SET_PAR_AND_F_PAR["PID_OFF"], 0)

    def on_adwin_pid(self):
        self.adw.Set_Par(SET_PAR_AND_F_PAR["ADWIN_PID_ON"], 1)

    def off_adwin_pid(self):
        self.adw.Set_Par(SET_PAR_AND_F_PAR["ADWIN_PID_OFF"], 0)

    def on_suicide_burn(self):
        self.suicide_burn = SuicideBurn(self.adw)
        self.adw.Set_Par(SET_PAR_AND_F_PAR["SB_ON"], 1)
        self.adw.Set_Par(SET_PAR_AND_F_PAR['EM'], 1)

    def off_suicide_burn(self):
        self.suicide_burn.stop_suicide_burn()
        self.adw.Set_Par(SET_PAR_AND_F_PAR["SB_OFF"], 0)
        self.adw.Set_Par(SET_PAR_AND_F_PAR['EM'], 0)

    def on_timer_event(self, window: LanderUI, repaint):
        self.data_values.add_new_vals_to_queue()
        window.update_sensor_values(self.data_values.queues)
        repaint()

    def manual_values_changed(self, ui_input: UIInputValue):
        self.adw.Set_Par(SET_PAR_AND_F_PAR["ATV1_ON"], ui_input.slider_atv1)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["PULSE_ON_ATV1"], ui_input.t_on_atv1)  # get t_on  from ui in ADwin
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["PULSE_OFF_ATV1"], ui_input.t_off_atv1)
        self.adw.Set_Par(SET_PAR_AND_F_PAR["ATV2_ON"], ui_input.slider_atv2)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["PULSE_ON_ATV2"], ui_input.t_on_atv2)  # get t_on  from ui in ADwin
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["PULSE_OFF_ATV2"], ui_input.t_off_atv2)
        self.adw.Set_Par(SET_PAR_AND_F_PAR["EM"], ui_input.slider_em)
        self.adw.Set_Par(SET_PAR_AND_F_PAR["SLIDER_H_COM"], ui_input.slider_h_com)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["H_0"], ui_input.initial_alt)

    def pid_values_changed(self, ui_input: UIInputValue):
        #self.adw.Set_Par(SET_PAR_AND_F_PAR["SLIDER_H_COM"], ui_input.slider_h_com)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["P_GAIN"], ui_input.p_gain)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["I_GAIN"], ui_input.i_gain)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["D_GAIN"], ui_input.d_gain)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["N_GAIN"], ui_input.n_gain)
        self.adw.Set_FPar(SET_PAR_AND_F_PAR["OMEGA_A"], ui_input.omega_a)
        #self.adw.Set_Par(SET_PAR_AND_F_PAR["SLIDER_H_COM"], ui_input.slider_h_com)
        #self.adw.Set_FPar(SET_PAR_AND_F_PAR["H_COM"], ui_input.h_com)

    #def suicide_burn_values_changed(self, ui_input: UIInputValue):
        #self.adw.Set_Par(SET_PAR_AND_F_PAR["SLIDER_H_COM"], ui_input.slider_h_com)
        #self.adw.Set_Par(SET_PAR_AND_F_PAR["H_0"], ui_input.initial_alt)

    def on_save(self, test_id): #Todo zwischenspeichern oder append, öfter auslesen
        directoryname = './' + 'Versuch_' + test_id
        directory = str(directoryname)
        parent_dir = "./Testergebnisse"
        os.chdir(str(parent_dir + directory))
        self.__data_save(TIME_FIFO, 'Time_data.txt')
        self.__data_save(SENSOR_FIFO, 'Sensor_data.txt')
        self.__data_save(ACTUATOR_FIFO, 'Actuator_data.txt')
        self.__data_save(THERMO_FIFO, 'Thermo_data.txt')
        os.chdir("../..")

    def __data_save(self, fifo_dict, filename):
        fifo_lengths = [self.adw.Fifo_Full(data_idx) for data_idx in fifo_dict.values()]
        min_fl = min(fl for fl in fifo_lengths if fl != 0)
        data_arrays = []
        header = []
        for name, val in fifo_dict.items():
            header.append(name)
            data_array = self.adw.GetFifo_Float(val, min_fl)
            data_arrays.append(np.ctypeslib.as_array(data_array))
        np.savetxt(filename, np.column_stack(data_arrays), header=','.join(header))