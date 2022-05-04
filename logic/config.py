# TODO: besser zusammenfassen

PROCESS_PATHS = {
    1: "./adwin/Merz_M11_Lander_Zeit_Initialisierung.TB1",  # bin files
    2: "./adwin/Merz_M11_Lander_Ansteuerung.TB2",
    4: "./adwin/Merz_M11_Lander_Messdatenerfassung_ADC.TB4",
    6: "./adwin/Merz_M11_Lander_Messdatenerfassung_Thermos.TB6",
}
SENSOR_PROCESS_IDS = [1, 4, 6]

NON_SENSOR_PROCESS_IDS = list(
    set(PROCESS_PATHS.keys()) - set(SENSOR_PROCESS_IDS))

TIME_FIFO = {
    "Time_nano": 1
}

SENSOR_FIFO = {
    "Time_Sensor": 140,
    "Pressure": 141,
    "Acceleration": 145,
    "Velocity_ACC": 151,
    "Velocity_H": 152,
    "Acceleration_H": 153,
    "Height": 156
}

THERMO_FIFO = {
    "Time_Thermo": 160,
    "Temperature": 161
}

ACTUATOR_FIFO = {
    "Time_Actuator": 120,
    "Pulse_ATV1": 121,
    "Pulse_ATV2": 122,
    "Altitude_Command": 130,
    "P_GAIN": 131,
    "I_Gain": 132,
    "D_Gain": 133,
    "N_Gain": 134,
    "OMEGA_A": 135,
    "ERROR": 136,
    "INTEGRAL_ERROR": 137,
    "DERIVATIVE_ERROR": 138,
    "CONTROL_U": 139
}

ALL_FIFO = TIME_FIFO | SENSOR_FIFO | THERMO_FIFO | ACTUATOR_FIFO

ACTUATOR_NAME_TO_ADWIN_PAR = {
    "E_MAGNET": 39,
    "ATV1": 25,
    "ATV2": 26,
}

SET_PAR_AND_F_PAR = {
    "ATV1_ON": 21,
    "PULSE_ON_ATV1": 21,
    "PULSE_OFF_ATV1": 22,
    "ATV2_ON": 23,
    "PULSE_ON_ATV2": 23,
    "PULSE_OFF_ATV2": 24,
    "SB_ON": 36,
    "SB_OFF": 36,
    "SEQUENCE_ON": 37,
    "PID_ON": 38,
    "PID_OFF": 38,
    'ADWIN_PID_ON': 35,
    'ADWIN_PID_OFF': 35,
    "EM": 39,
    "SLIDER_H_COM": 30,
    "H_COM": 30,
    "H_0": 29,
    "P_GAIN": 31,
    "I_GAIN": 32,
    "D_GAIN": 33,
    "N_GAIN": 34,
    "OMEGA_A": 35,
    "ALTITUDE": 56
}

GLOBAL_ADWIN_FPAR = {
    # ADwin is 1 based
    'TIME_ADWIN': 0,
    'TIME_CONTROL': 20,
    'ALTITUDE_COM': 29,
    'TIMETOBURN_COM': 56,
    'BURNTIME_COM': 57,
    'BURNALTITUDE_COM': 58,
    "H_COM": 30,
    "P_GAIN": 31,
    "I_GAIN": 32,
    "D_GAIN": 33,
    "N_GAIN": 34,
    "OMEGA_A": 35,
    'PRESSURE': 41,
    'TEMPERATURE': 60,
    'ALTITUDE': 55,
    'ALTITUDE_ACC': 49,
    'ACCELERATION_H': 52,
    'VELOCITY_H': 51,
    'VELOCITY_ACC': 50,
    'ACCELERATION': 44,
    'ATV1': 21,
    'ATV2': 23
}

CONTROL = {
    'ATV1': 25,
    'ATV2': 26,
    'H_COM': 30,
    'P_GAIN': 31,
    'I_GAIN': 32,
    'D_GAIN': 33,
    'N_GAIN': 34,
    'OMEGA_A': 35,
    'ERROR': 36,
    'INTEGRAL_ERROR': 37,
    'DERIVATIVE_ERROR': 38,
    'CONTROL_U': 39,
    'H_MEAS': 55,
    'TIMETOBURN': 57,
    'BURNTIME': 58,
    'BURNALTITUDE': 59,
}
