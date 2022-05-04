'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = RA-TRS120  DLR\merz_fo
'<Header End>
'=============================================================================================================================
'AdBasic Skript Temperatur, Druck, Abstand, Beschleunigung

'Stand: 29.11.2021
'Florian Merz

'==================================================
'Informationen

' TIME: 
'           Par:  -
'           FPar: 1
'           Data: 1
' Zeit Ansteuerung TRA:
'           Par:  -
'           FPar: 20
'           Data: 120
' Zeit Sensoren AIn:
'           Par:  -
'           FPar: 40
'           Data: 140
' Zeit Temperatur:
'           Par:  -
'           FPar: 60
'           Data: 160

'=============================================================================================================================
#Include ADwinPro_All.Inc

Dim Data_1[500003] as Float as fifo
Dim Abtastfrequenz_Hz_TIME as Float

Init:
  
  Processdelay = 2000 

  
  ' Zeit-Parameter TIME
  FPar_1 = 0
  
  Fifo_clear(1)
  
  Abtastfrequenz_Hz_TIME = 1/(Processdelay*3.333333333333333333333*1e-9)

Event:

  'Zeitstempel berechnen/ schreiben und an alle anderen Prozesse weiterreichen
  FPar_1 = FPar_1 + 1/Abtastfrequenz_Hz_TIME
  Data_1 = FPar_1
