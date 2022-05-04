'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 5
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
#Include ADwinPro_All.Inc

'Zeit
Dim Zeit_AIn as Float

'<Region> "Datenfeld Zeit"
Dim Data_140[100003] as Float as fifo
'<Endregion>

'AIn Modul 1 RackPos 4
Dim AIn_Modulnummer_1 as Integer

'<Region> "Datenfelder Pins/Kanäle"
Dim Data_141[100003] as Float as fifo  
Dim Data_142[100003] as Float as fifo  
Dim Data_143[100003] as Float as fifo  
Dim Data_144[100003] as Float as fifo  
Dim Data_145[100003] as Float as fifo  
Dim Data_146[100003] as Float as fifo  
Dim Data_147[100003] as Float as fifo  
Dim Data_148[100003] as Float as fifo  
Dim Data_149[100003] as Float as fifo  
Dim Data_150[100003] as Float as fifo  
Dim Data_151[100003] as Float as fifo  
Dim Data_152[100003] as Float as fifo
Dim Data_153[100003] as Float as fifo  
Dim Data_154[100003] as Float as fifo  
Dim Data_155[100003] as Float as fifo
Dim Data_156[100003] as Float as fifo
'<Endregion>

'AIn-32/18 Kanäle 1-16
'<Region> "Modul1"
Dim Kanal_1_01 as Float
Dim Kanal_1_02 as Float
Dim Kanal_1_03 as Float
Dim Kanal_1_04 as Float
Dim Kanal_1_05 as Float
Dim Kanal_1_06 as Float
Dim Kanal_1_07 as Float
Dim Kanal_1_08 as Float
Dim Kanal_1_09 as Float
Dim Kanal_1_10 as Float
Dim Kanal_1_11 as Float
Dim Kanal_1_12 as Float
Dim Kanal_1_13 as Float
Dim Kanal_1_14 as Float
Dim Kanal_1_15 as Float
Dim Kanal_1_16 as Float
'<Endregion>
Init:
  'RackPos des Moduls
  AIn_Modulnummer_1 = 4
    
'<Region> Zeit-Parameter Temperaturen
  Fifo_clear(140)
'<Endregion>
  
'<Region> "Modul 1"
  Fifo_clear(141)
  Fifo_clear(142)
  Fifo_clear(143)
  Fifo_clear(144)
  Fifo_clear(145)
  Fifo_clear(146)
  Fifo_clear(147)
  Fifo_clear(148)
  Fifo_clear(149)
  Fifo_clear(150)
  Fifo_clear(151)
  Fifo_clear(152)
  Fifo_clear(153)
  Fifo_clear(154)
  Fifo_clear(155)
  Fifo_clear(156)
'<Endregion>

  '  P2_Seq_Init(AIn_Modulnummer_1, 0,0,0,0)
  '  P2_Set_Mux(AIn_Modulnummer_1, 0b)
  '  P2_Wait_Mux(AIn_Modulnummer_1)
  '  P2_Start_Conv(AIn_Modulnummer_1)
  '  P2_Set_Mux(AIn_Modulnummer_1, 0011b)
  '  P2_Wait_EOC(AIn_Modulnummer_1)
  
  Processdelay = 300000000
  
  
Event:

  'LED der Module anschalten
  if (Par_2 >= 0) then
    P2_Set_LED(AIn_Modulnummer_1,1)
  else
    P2_Set_LED(AIn_Modulnummer_1,0)
  endif
  
  
  'Zeit-Parameter MF
  FPar_40 = FPar_1
  Data_140 = FPar_40 
  
  '"Modul 4 Kanal 1-16"
  
  '  
'<Region> "Modul 4 Kanal 4" Beschleunigungssensor
  Par_44 = P2_ADC24(AIn_Modulnummer_1,4)
  'Abfrage mit 24 Bit, Modul liest mit 18 Bit, daher Rechtsverschiebung (Bitshift) um 6 Stellen
  Par_44 = Shift_Right(Par_44,0)
  Kanal_1_04 = Par_44
  FPar_44 = 20*(Kanal_1_04/2^24)-10  'weil Adwin abweichungen hat - 0.01
  FPar_45 = FPar_44/0.01618
  Kanal_1_04 = FPar_44
  Kanal_1_05 = FPar_45
  Data_144 = Kanal_1_04
  Data_145 = Kanal_1_05
'<Endregion>
  '
  P2_Wait_Mux(AIn_Modulnummer_1)
  P2_Start_Conv(AIn_Modulnummer_1)
          
  P2_Set_Mux(AIn_Modulnummer_1, 1001b)
  P2_Wait_EOC(AIn_Modulnummer_1)
  
'<Region> "Modul 4 Kanal 16" Abstandssensor
  Par_56 = P2_ADC24(AIn_Modulnummer_1,16)
  'Abfrage mit 24 Bit, Modul liest mit 16 Bit, daher Rechtsverschiebung (Bitshift) um 6 Stellen
  Par_56 = Shift_Right(Par_56,8)
  Kanal_1_16 = Par_56
  FPar_56 = 20*(Kanal_1_16/2^16)-10
  Kanal_1_16 = FPar_56 ' 1 Volt entspricht 1m / 0,1V entspricht 10cm
  Data_156 = Kanal_1_16
'<Endregion>
 
  '  P2_Wait_Mux(AIn_Modulnummer_1)
  '  P2_Start_Conv(AIn_Modulnummer_1)
  '  
  '  P2_Set_Mux(AIn_Modulnummer_1, 1001b)
  '  P2_Wait_EOC(AIn_Modulnummer_1)
  '  
  '  P2_Wait_Mux(AIn_Modulnummer_1)
  '  P2_Start_Conv(AIn_Modulnummer_1)
  '              
  '  P2_Set_Mux(AIn_Modulnummer_1, 0011b)
  '  P2_Wait_EOC(AIn_Modulnummer_1)
  
'<Region> "Modul 4 Kanal 10" Drucksensor
  Par_41 = P2_ADC24(AIn_Modulnummer_1,10)
  'Abfrage mit 24 Bit, Modul liest mit 18 Bit, daher Rechtsverschiebung (Bitshift) um 6 Stellen
  Par_41 = Shift_Right(Par_41,6)
  Kanal_1_01 = Par_41
  FPar_41 = 20*(Kanal_1_01/2^18)-10 
  'Druckpolynom
  FPar_42 = 7.419605321320829e-06 * FPar_41^4 + 1.151875980614826e-04 * FPar_41^3 -0.003608840831045 * FPar_41^2 + 10.036314651348565 * FPar_41 -0.090362785744654 
  Kanal_1_01 = FPar_42
  Data_141 = Kanal_1_01
'<Endregion>

  '  P2_Wait_Mux(AIn_Modulnummer_1)
  '  P2_Start_Conv(AIn_Modulnummer_1)
  '  
  '  P2_Set_Mux(AIn_Modulnummer_1, 1001b)
  '  P2_Wait_EOC(AIn_Modulnummer_1)
     
  '  P2_Wait_Mux(AIn_Modulnummer_1)
  '  P2_Start_Conv(AIn_Modulnummer_1)
  '            
  '  P2_Set_Mux(AIn_Modulnummer_1, 1111b)
  '  P2_Wait_EOC(AIn_Modulnummer_1)
  
  P2_Wait_Mux(AIn_Modulnummer_1)
  P2_Start_Conv(AIn_Modulnummer_1)
              
  P2_Set_Mux(AIn_Modulnummer_1, 0011b)
  P2_Wait_EOC(AIn_Modulnummer_1)
  
  

  

  
  '
  '  Data_151 = FPar_51
  '  Data_152 = FPar_52
  '  Data_153 = FPar_53

  

  'Velocity from Height
  'v0 = 0
  'velocity = []
  'velocity = ((Data_155[last_value]-Data_155[last_value -1])/(Data_140[last_value]-Data_140[last_value -1])) - velocity[last_value] 
  'FPar_52 = velocity
