from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from logic.config import *
import os
from dataclasses import dataclass


class LanderUI(QtWidgets.QMainWindow):
    PLOT_X_PERIOD_SECS = 5.0  # the span of the x axis of all plots, in seconds

    def __init__(self, event_handler):
        super(LanderUI, self).__init__()
        self.event_handler = event_handler
        self.next_test_id = ""

        # Load UI
        uic.loadUi('qt_ui/app.ui', self)

        # Initialisiere UI
        self.__initialize_plots()
        self.__launch_buttons()

    def boot(self):
        self.event_handler.on_boot()
        self.BootButton.setEnabled(False)
        self.StartButton.setEnabled(True)

    def quit(self):
        self.__set_slider_zero()
        self.event_handler.on_quit(self.next_test_id)
        self.close()

    def start(self):
        self.event_handler.on_start()
        self.__start_buttons()
        self.__enable_manual_action()
        self.__enable_pid_control()
        self.doubleSpinBox_Abtastfrequenz.setValue(166)
        self.doubleSpinBox_t_on_atv1.setValue(0.100)
        self.doubleSpinBox_t_off_atv1.setValue(0.050)
        self.doubleSpinBox_t_on_atv2.setValue(0.200)
        self.doubleSpinBox_t_off_atv2.setValue(0.075)
        self.doubleSpinBox_PGain.setValue(60)
        self.doubleSpinBox_IGain.setValue(120)
        self.doubleSpinBox_DGain.setValue(7.5)

    def stop(self):
        self.__stop_buttons()
        self.__set_slider_zero()
        self.event_handler.on_stop(self.next_test_id)
        self.lineEdit_testnumber.setText("")
        self.next_test_id = ""

    def save(self):
        if self.lineEdit_testnumber.isModified():
            self.lineEdit_testnumber.setStyleSheet(f"color: black; background-color: white")
            self.__check_and_set_test_id()
        else:
            self.lineEdit_testnumber.setStyleSheet(f"color: black; background-color: red")

    def pid_on(self):
        self.save()
        self.event_handler.on_pid()
        self.__pid_on_buttons()
        self.verticalSlider_ATV1.triggerAction(5)
        self.verticalSlider_ATV2.triggerAction(5)  # setzt Slider auf 0
        # P= 8, I = 5, D = 10

    def pid_off(self):
        self.event_handler.off_pid()
        self.__pid_off_buttons()
        self.verticalSlider_ATV1.triggerAction(6)  # setzt Slider auf 1
        self.doubleSpinBox_t_on_atv1.setValue(0.100)
        self.doubleSpinBox_t_off_atv1.setValue(0.050)
        self.verticalSlider_ATV2.triggerAction(6)  # setzt Slider auf 1
        self.doubleSpinBox_t_on_atv2.setValue(0.100)
        self.doubleSpinBox_t_off_atv2.setValue(0.075)

    def adwin_pid_on(self):
        self.save()
        self.event_handler.on_adwin_pid()
        self.__adwin_pid_on_buttons()
        self.verticalSlider_ATV1.triggerAction(5)
        self.verticalSlider_ATV2.triggerAction(5)  # setzt Slider auf 0
        # P= 8, I = 5, D = 10

    def adwin_pid_off(self):
        self.event_handler.off_adwin_pid()
        self.__adwin_pid_off_buttons()
        self.verticalSlider_ATV1.triggerAction(6)  # setzt Slider auf 1
        self.doubleSpinBox_t_on_atv1.setValue(0.100)
        self.doubleSpinBox_t_off_atv1.setValue(0.050)
        self.verticalSlider_ATV2.triggerAction(6)  # setzt Slider auf 1
        self.doubleSpinBox_t_on_atv2.setValue(0.100)
        self.doubleSpinBox_t_off_atv2.setValue(0.075)

    def sequence_on(self):
        self.SequenceOnButton.setEnabled(False)
        self.SequenceOffButton.setEnabled(True)
        self.event_handler.on_sequence()

    def sequence_off(self):
        self.SequenceOnButton.setEnabled(True)
        self.SequenceOffButton.setEnabled(False)
        self.event_handler.off_sequence()

    def suicide_burn_on(self):
        self.save()
        self.event_handler.on_suicide_burn()
        self.__sb_on_buttons()
        self.verticalSlider_ATV1.triggerAction(5)
        self.verticalSlider_ATV2.triggerAction(5)  # setzt Slider auf 0

    def suicide_burn_off(self):
        self.event_handler.off_suicide_burn()
        self.__sb_off_buttons()
        self.verticalSlider_ATV1.triggerAction(6)  # setzt Slider auf 1
        self.doubleSpinBox_t_on_atv1.setValue(0.100)
        self.doubleSpinBox_t_off_atv1.setValue(0.050)
        self.verticalSlider_ATV2.triggerAction(6)  # setzt Slider auf 1
        self.doubleSpinBox_t_on_atv2.setValue(0.100)
        self.doubleSpinBox_t_off_atv2.setValue(0.075)

    def __set_slider_zero(self):
        self.horizontalSlider_EM.triggerAction(5)  # setzt Slider auf 0
        self.verticalSlider_ATV1.triggerAction(5)
        self.verticalSlider_ATV2.triggerAction(5)
        self.verticalSlider_Altitude.triggerAction(5)

    def __enable_manual_action(self):
        self.__set_slider_zero()
        self.horizontalSlider_EM.valueChanged.connect(self.on_manual_values_changed)
        self.verticalSlider_ATV1.valueChanged.connect(self.on_manual_values_changed)
        self.verticalSlider_ATV2.valueChanged.connect(self.on_manual_values_changed)
        self.doubleSpinBox_t_on_atv1.valueChanged.connect(self.on_manual_values_changed)
        self.doubleSpinBox_t_off_atv1.valueChanged.connect(self.on_manual_values_changed)
        self.doubleSpinBox_t_on_atv2.valueChanged.connect(self.on_manual_values_changed)
        self.doubleSpinBox_t_off_atv2.valueChanged.connect(self.on_manual_values_changed)
        self.verticalSlider_Altitude.valueChanged.connect(self.on_manual_values_changed)
        self.doubleSpinBox_h0.valueChanged.connect(self.on_manual_values_changed)

    def on_manual_values_changed(self):
        self.event_handler.manual_values_changed(self.get_ui_input())

    def __enable_pid_control(self):
        #self.doubleSpinBox_h_com.valueChanged.connect(self.on_pid_values_changed)
        #self.verticalSlider_Altitude.valueChanged.connect(self.on_pid_values_changed)
        self.doubleSpinBox_PGain.valueChanged.connect(self.on_pid_values_changed)
        self.doubleSpinBox_IGain.valueChanged.connect(self.on_pid_values_changed)
        self.doubleSpinBox_DGain.valueChanged.connect(self.on_pid_values_changed)
        self.doubleSpinBox_NGain.valueChanged.connect(self.on_pid_values_changed)
        self.doubleSpinBox_Abtastfrequenz.valueChanged.connect(self.on_pid_values_changed)

    def on_pid_values_changed(self):
        #self.doubleSpinBox_h_com.setValue(self.verticalSlider_Altitude.value()/100)
        self.event_handler.pid_values_changed(self.get_ui_input())

    def __enable_ai_control(self):
        pass

    def ki_on(self):
        pass

    def ki_off(self):
        pass

    def __check_and_set_test_id(self):
        self.next_test_id = self.lineEdit_testnumber.text()
        directoryname = 'Versuch_' + self.next_test_id
        directory = str(directoryname)
        parent_dir = "./Testergebnisse"
        newpath = os.path.join(parent_dir, directory)
        if os.path.exists(newpath):
            self.lineEdit_testnumber.setStyleSheet("color: black;  background-color: red")
            self.lineEdit_testnumber.setText("Testnumber exists")
        else:
            os.chdir(parent_dir)
            os.chdir('../')
            os.makedirs(newpath)
            self.SaveButton.setEnabled(False)
            self.SaveButton.setStyleSheet("color: red")
            self.event_handler.clear_fifo()

    def __launch_buttons(self):
        self.BootButton.clicked.connect(self.boot)
        self.QuitButton.clicked.connect(self.quit)
        self.StartButton.clicked.connect(self.start)
        self.StopButton.clicked.connect(self.stop)
        self.SaveButton.clicked.connect(self.save)
        self.PIDONButton.clicked.connect(self.pid_on)
        self.PIDOFFButton.clicked.connect(self.pid_off)
        self.ADWINPIDONButton.clicked.connect(self.adwin_pid_on)
        self.ADWINPIDOFFButton.clicked.connect(self.adwin_pid_off)
        self.KIONButton.clicked.connect(self.ki_on)
        self.KIOFFButton.clicked.connect(self.ki_off)
        self.SBONButton.clicked.connect(self.suicide_burn_on)
        self.SBOFFButton.clicked.connect(self.suicide_burn_off)
        self.SequenceOnButton.clicked.connect(self.sequence_on)
        self.SequenceOffButton.clicked.connect(self.sequence_off)
        self.StartButton.setEnabled(False)
        self.StopButton.setEnabled(False)
        self.PIDONButton.setEnabled(False)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(False)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(False)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(False)
        self.SBOFFButton.setEnabled(False)
        self.SaveButton.setEnabled(False)
        self.SequenceOnButton.setEnabled(False)
        self.SequenceOffButton.setEnabled(False)
        self.horizontalSlider_EM.setEnabled(False)
        self.verticalSlider_ATV1.setEnabled(False)
        self.verticalSlider_ATV2.setEnabled(False)
        self.verticalSlider_Altitude.setEnabled(False)
        #self.doubleSpinBox_h_com.setEnabled(False)
        self.doubleSpinBox_PGain.setEnabled(False)
        self.doubleSpinBox_IGain.setEnabled(False)
        self.doubleSpinBox_DGain.setEnabled(False)
        self.doubleSpinBox_NGain.setEnabled(False)
        self.doubleSpinBox_h0.setEnabled(False)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(False)
        self.doubleSpinBox_t_on_atv1.setEnabled(False)
        self.doubleSpinBox_t_off_atv1.setEnabled(False)
        self.doubleSpinBox_t_on_atv2.setEnabled(False)
        self.doubleSpinBox_t_off_atv2.setEnabled(False)
        self.PlotWidget_altitude.setEnabled(False)
        self.PlotWidget_velocity.setEnabled(False)
        self.PlotWidget_acceleration.setEnabled(False)

    def __start_buttons(self):
        # Buttons
        self.StartButton.setEnabled(False)
        self.StopButton.setEnabled(True)
        self.QuitButton.setEnabled(True)
        self.PIDONButton.setEnabled(True)
        self.ADWINPIDONButton.setEnabled(True)
        self.KIONButton.setEnabled(True)
        self.SBONButton.setEnabled(True)
        self.SaveButton.setEnabled(True)
        self.SaveButton.setStyleSheet("color: black")
        self.SequenceOnButton.setEnabled(True)
        # Insert
        self.horizontalSlider_EM.setEnabled(True)
        self.verticalSlider_ATV1.setEnabled(True)
        self.verticalSlider_ATV2.setEnabled(True)
        self.verticalSlider_Altitude.setEnabled(True)
        #self.doubleSpinBox_h_com.setEnabled(True)
        self.doubleSpinBox_PGain.setEnabled(True)
        self.doubleSpinBox_IGain.setEnabled(True)
        self.doubleSpinBox_DGain.setEnabled(True)
        self.doubleSpinBox_NGain.setEnabled(True)
        self.doubleSpinBox_h0.setEnabled(True)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(True)
        self.doubleSpinBox_t_on_atv1.setEnabled(True)
        self.doubleSpinBox_t_off_atv1.setEnabled(True)
        self.doubleSpinBox_t_on_atv2.setEnabled(True)
        self.doubleSpinBox_t_off_atv2.setEnabled(True)

    def __stop_buttons(self):
        # Buttons
        self.BootButton.setEnabled(True)
        self.StartButton.setEnabled(True)
        self.StopButton.setEnabled(False)
        self.QuitButton.setEnabled(True)
        self.PIDONButton.setEnabled(False)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(False)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(False)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(False)
        self.SBOFFButton.setEnabled(False)
        self.SaveButton.setEnabled(False)
        self.SaveButton.setStyleSheet("color: grey")
        self.SequenceOnButton.setEnabled(False)
        self.SequenceOffButton.setEnabled(False)
        # Insert
        self.horizontalSlider_EM.setEnabled(False)
        self.verticalSlider_ATV1.setEnabled(False)
        self.verticalSlider_ATV2.setEnabled(False)
        self.verticalSlider_Altitude.setEnabled(False)
        #self.doubleSpinBox_h_com.setEnabled(False)
        self.doubleSpinBox_PGain.setEnabled(False)
        self.doubleSpinBox_IGain.setEnabled(False)
        self.doubleSpinBox_DGain.setEnabled(False)
        self.doubleSpinBox_NGain.setEnabled(False)
        self.doubleSpinBox_h0.setEnabled(False)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(False)
        self.doubleSpinBox_t_on_atv1.setEnabled(False)
        self.doubleSpinBox_t_off_atv1.setEnabled(False)
        self.doubleSpinBox_t_on_atv2.setEnabled(False)
        self.doubleSpinBox_t_off_atv2.setEnabled(False)

    def __pid_on_buttons(self):
        self.PIDONButton.setEnabled(False)
        self.PIDOFFButton.setEnabled(True)
        self.ADWINPIDONButton.setEnabled(False)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(False)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(False)
        self.SBOFFButton.setEnabled(False)
        self.doubleSpinBox_PGain.setEnabled(True)
        self.doubleSpinBox_IGain.setEnabled(True)
        self.doubleSpinBox_DGain.setEnabled(True)
        self.doubleSpinBox_NGain.setEnabled(False)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(False)
        self.verticalSlider_ATV1.setEnabled(False)
        self.doubleSpinBox_t_on_atv1.setEnabled(False)
        self.doubleSpinBox_t_off_atv1.setEnabled(False)
        self.verticalSlider_ATV2.setEnabled(False)
        self.doubleSpinBox_t_on_atv2.setEnabled(False)
        self.doubleSpinBox_t_off_atv2.setEnabled(False)

    def __pid_off_buttons(self):
        self.PIDONButton.setEnabled(True)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(True)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(True)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(True)
        self.SBOFFButton.setEnabled(False)
        self.doubleSpinBox_PGain.setEnabled(True)
        self.doubleSpinBox_IGain.setEnabled(True)
        self.doubleSpinBox_DGain.setEnabled(True)
        self.doubleSpinBox_NGain.setEnabled(True)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(True)
        self.verticalSlider_ATV1.setEnabled(True)
        self.doubleSpinBox_t_on_atv1.setEnabled(True)
        self.doubleSpinBox_t_off_atv1.setEnabled(True)
        self.verticalSlider_ATV2.setEnabled(True)
        self.doubleSpinBox_t_on_atv2.setEnabled(True)
        self.doubleSpinBox_t_off_atv2.setEnabled(True)

    def __adwin_pid_on_buttons(self):
        self.PIDONButton.setEnabled(False)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(False)
        self.ADWINPIDOFFButton.setEnabled(True)
        self.KIONButton.setEnabled(False)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(False)
        self.SBOFFButton.setEnabled(False)
        self.doubleSpinBox_PGain.setEnabled(True)
        self.doubleSpinBox_IGain.setEnabled(True)
        self.doubleSpinBox_DGain.setEnabled(True)
        self.doubleSpinBox_NGain.setEnabled(False)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(False)
        self.verticalSlider_ATV1.setEnabled(False)
        self.doubleSpinBox_t_on_atv1.setEnabled(False)
        self.doubleSpinBox_t_off_atv1.setEnabled(False)
        self.verticalSlider_ATV2.setEnabled(False)
        self.doubleSpinBox_t_on_atv2.setEnabled(False)
        self.doubleSpinBox_t_off_atv2.setEnabled(False)

    def __adwin_pid_off_buttons(self):
        self.PIDONButton.setEnabled(True)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(True)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(True)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(True)
        self.SBOFFButton.setEnabled(False)
        self.doubleSpinBox_PGain.setEnabled(True)
        self.doubleSpinBox_IGain.setEnabled(True)
        self.doubleSpinBox_DGain.setEnabled(True)
        self.doubleSpinBox_NGain.setEnabled(True)
        self.doubleSpinBox_Abtastfrequenz.setEnabled(True)
        self.verticalSlider_ATV1.setEnabled(True)
        self.doubleSpinBox_t_on_atv1.setEnabled(True)
        self.doubleSpinBox_t_off_atv1.setEnabled(True)
        self.verticalSlider_ATV2.setEnabled(True)
        self.doubleSpinBox_t_on_atv2.setEnabled(True)
        self.doubleSpinBox_t_off_atv2.setEnabled(True)

    def __sb_on_buttons(self):
        self.PIDONButton.setEnabled(False)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(False)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(False)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(False)
        self.SBOFFButton.setEnabled(True)
        self.doubleSpinBox_h0.setEnabled(False)
        self.verticalSlider_ATV1.setEnabled(False)
        self.doubleSpinBox_t_on_atv1.setEnabled(False)
        self.doubleSpinBox_t_off_atv1.setEnabled(False)
        self.verticalSlider_ATV2.setEnabled(False)
        self.doubleSpinBox_t_on_atv2.setEnabled(False)
        self.doubleSpinBox_t_off_atv2.setEnabled(False)

    def __sb_off_buttons(self):
        self.PIDONButton.setEnabled(True)
        self.PIDOFFButton.setEnabled(False)
        self.ADWINPIDONButton.setEnabled(True)
        self.ADWINPIDOFFButton.setEnabled(False)
        self.KIONButton.setEnabled(True)
        self.KIOFFButton.setEnabled(False)
        self.SBONButton.setEnabled(True)
        self.SBOFFButton.setEnabled(False)
        self.doubleSpinBox_h0.setEnabled(True)
        self.verticalSlider_ATV1.setEnabled(True)
        self.doubleSpinBox_t_on_atv1.setEnabled(True)
        self.doubleSpinBox_t_off_atv1.setEnabled(True)
        self.verticalSlider_ATV2.setEnabled(True)
        self.doubleSpinBox_t_on_atv2.setEnabled(True)
        self.doubleSpinBox_t_off_atv2.setEnabled(True)

    def __initialize_plots(self):
        # Legend
        self.PlotWidget_altitude.addLegend(offset=1)
        self.PlotWidget_velocity.addLegend(offset=1)
        self.PlotWidget_acceleration.addLegend(offset=1)
        # Title
        self.PlotWidget_altitude.setTitle("Höhe", color="k", size="15pt")
        self.PlotWidget_velocity.setTitle("Geschwindigkeit", color="k", size="15pt")
        self.PlotWidget_acceleration.setTitle("Beschleunigung", color="k", size="15pt")
        # Style
        styles = {'color': 'r', 'font-size': '10pt'}
        # Label
        self.PlotWidget_altitude.setLabel('left', 'h (m)', **styles)
        self.PlotWidget_altitude.setLabel('bottom', 'Zeit (s)', **styles)
        self.PlotWidget_velocity.setLabel('left', 'v (m/s)', **styles)
        self.PlotWidget_velocity.setLabel('bottom', 'Zeit (s)', **styles)
        self.PlotWidget_acceleration.setLabel('left', 'a (m/s²)', **styles)
        self.PlotWidget_acceleration.setLabel('bottom', 'Zeit (s)', **styles)
        # Background
        self.PlotWidget_altitude.setBackground('w')
        self.PlotWidget_velocity.setBackground('w')
        self.PlotWidget_acceleration.setBackground('w')
        # Grid
        self.PlotWidget_altitude.showGrid(x=True, y=True)
        self.PlotWidget_velocity.showGrid(x=True, y=True)
        self.PlotWidget_acceleration.showGrid(x=True, y=True)
        # Plot
        x = [0, 1, 2]
        h = [0, 1, 6]
        v = [0, 1, 10]
        a = [0, 1, 30]
        pen1 = pg.mkPen(color='r')
        pen2 = pg.mkPen(color='b')
        pen3 = pg.mkPen(color='g')
        self.default_pen = pen1
        self.dataline_altitude = self.PlotWidget_altitude.plot(x, h, name='h', pen=pen2)
        #self.dataline_altitude_acc = self.PlotWidget_altitude.plot(x, h, name='h', pen=pen1)
        self.dataline_velocity_h = self.PlotWidget_velocity.plot(x, v, name='v aus h', pen=pen2)
        #self.dataline_velocity_acc = self.PlotWidget_velocity.plot(x, v, name='v aus a', pen=pen1)
        self.dataline_acceleration = self.PlotWidget_acceleration.plot(x, a, name='a', pen=pen2)
        #self.dataline_acceleration_h = self.PlotWidget_acceleration.plot(x, a, name='a aus h', pen=pen1)
        self.PlotWidget_acceleration.setYRange(5, -15)
        self.__draw_dataline()

    def __draw_dataline(self):
        self.dataline_to_fpar_identifier = {
            self.dataline_altitude: 'ALTITUDE',
            #self.dataline_altitude_acc: 'ALTITUDE_ACC',
            self.dataline_velocity_h: 'VELOCITY_H',
            #self.dataline_velocity_acc: 'VELOCITY_ACC',
            self.dataline_acceleration: 'ACCELERATION',
            #self.dataline_acceleration_h: 'ACCELERATION_H',
        }

    def update_sensor_values(self, values: list[list[float]]):  # TODO plots updaten nicht richtig
        time_series = values[list(GLOBAL_ADWIN_FPAR.keys()).index('TIME_ADWIN')]

        t_min = time_series[-1] - LanderUI.PLOT_X_PERIOD_SECS
        # print("Timeseries von -1", time_series[-1])
        try:  ### Wenn ich das richtig sehe, ist dieser Try-Catch overkill. Sowas würde ich vermeiden, wenn es anders geht. z.B. duch einen Check der Länge oder der erlaubten variablen
            first_index = next(i for i, val in enumerate(time_series) if
                               val >= t_min)  ### What the hell is even that? Ich weiß, dass sowas geht, aber das heißt nicht, dass man sowas tun sollte... :D
        except StopIteration:
            first_index = 0
        plot_indices_slice = slice(first_index, len(time_series))
        for (dataline, identifier) in self.dataline_to_fpar_identifier.items():
            dataline.setData(time_series[plot_indices_slice], \
                             values[list(GLOBAL_ADWIN_FPAR.keys()).index(identifier)][plot_indices_slice])

        self.update_lcd_values(values)

    def update_lcd_values(self, values):
        self.lcdNumber_time.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('TIME_ADWIN')][-1])
        self.lcdNumber_altitude.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('ALTITUDE')][-1])
        self.lcdNumber_timetoburn_com.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('TIMETOBURN_COM')][-1])
        self.lcdNumber_burntime_com.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('BURNTIME_COM')][-1])
        self.lcdNumber_altitude_com.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('ALTITUDE_COM')][-1])
        self.lcdNumber_burnaltitude_com.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('BURNALTITUDE_COM')][-1])
        self.lcdNumber_velocity.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('VELOCITY_H')][-1])
        self.lcdNumber_acceleration.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('ACCELERATION')][-1])
        self.lcdNumber_temperature.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('TEMPERATURE')][-1])
        self.lcdNumber_pressure.display(values[list(GLOBAL_ADWIN_FPAR.keys()).index('PRESSURE')][-1])

    def get_ui_input(self):
        return UIInputValue(slider_atv1=self.verticalSlider_ATV1.value(),
                            slider_atv2=self.verticalSlider_ATV2.value(),
                            t_on_atv1=self.doubleSpinBox_t_on_atv1.value(),
                            t_off_atv1=self.doubleSpinBox_t_off_atv1.value(),
                            t_on_atv2=self.doubleSpinBox_t_on_atv2.value(),
                            t_off_atv2=self.doubleSpinBox_t_off_atv2.value(),
                            slider_em=self.horizontalSlider_EM.value(),
                            p_gain=self.doubleSpinBox_PGain.value(),
                            i_gain=self.doubleSpinBox_IGain.value(),
                            d_gain=self.doubleSpinBox_DGain.value(),
                            n_gain=self.doubleSpinBox_NGain.value(),
                            omega_a=self.doubleSpinBox_Abtastfrequenz.value(),
                            slider_h_com=self.verticalSlider_Altitude.value(),
                            initial_alt=self.doubleSpinBox_h0.value())


@dataclass()
class UIInputValue:
    slider_atv1: int
    slider_atv2: int
    t_on_atv1: int
    t_off_atv1: int
    t_on_atv2: int
    t_off_atv2: int
    slider_em: int
    p_gain: int
    i_gain: int
    d_gain: int
    n_gain: int
    omega_a: int
    slider_h_com: int
    initial_alt: int

