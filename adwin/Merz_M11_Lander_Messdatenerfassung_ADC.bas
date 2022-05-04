'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = No
' Stacksize                      = 1000
' Info_Last_Save                 = RA-TRS120  DLR\merz_fo
'<Header End>
#Include ADwinPro_All.Inc

'Zeit
Dim Abtastfrequenz_Hz_AIn as Float

'AIn Modul 1 RackPos 4
Dim AIn_Modulnummer_1 as Integer

'<Region> "Datenfeld Zeit"
Dim Data_140[500003] as Float as fifo
'<Endregion>

'<Region> "Datenfelder Pins/Kanäle"
Dim Data_141[500003] as Float as fifo  
Dim Data_142[500003] as Float as fifo  
Dim Data_143[500003] as Float as fifo  
Dim Data_144[500003] as Float as fifo  
Dim Data_145[500003] as Float as fifo  
Dim Data_146[500003] as Float as fifo  
Dim Data_147[500003] as Float as fifo  
Dim Data_148[500003] as Float as fifo  
Dim Data_149[500003] as Float as fifo  
Dim Data_150[500003] as Float as fifo  
Dim Data_151[500003] as Float as fifo  
Dim Data_152[500003] as Float as fifo
Dim Data_153[500003] as Float as fifo  
Dim Data_154[500003] as Float as fifo  
Dim Data_155[500003] as Float as fifo
Dim Data_156[500003] as Float as fifo
Dim value[100000] as Float  
'<Endregion>

'AIn-32/18 Kanäle 1-16
'<Region> "Modul 4"
Dim Kanal_4_04 as Float
Dim Kanal_4_10 as Float
Dim Kanal_4_16 as Float
Dim Druck as Float
Dim Beschleunigung as Float

Dim Ts as Float
Dim acc as Float
Dim a as Float
Dim acc1 as Float
Dim velocity_a as Float
Dim acceleration_h as Float
Dim altitude_acc as Float
Dim h as Float
Dim h1 as Float
Dim h0 as Float
Dim t1 as float
Dim t as float
Dim velocity as float
'<Endregion>

Init:
  
  'RackPos des Moduls
  AIn_Modulnummer_1 = 4
  
  Abtastfrequenz_Hz_AIN = 1/(ProcessDelay*3.333333333333333333333*1e-9)
    
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
  
  Processdelay = 300000
  
  'Mux liest zu schnell aus, Kondensatoren werden nicht ganz geladen. (1.500 * 20ns + 2.000ns = 32.000 ns) 
  P2_Seq_Init(4, 0,0, 0, 1500)
  
Event:

  'LED der Module anschalten
  P2_Set_LED(AIn_Modulnummer_1,1)
  
  'Zeit-Parameter 
  FPar_40 = FPar_1
  Data_140 = FPar_40 
  
  Ts = 1/Abtastfrequenz_Hz_AIn
  
  '"Modul 4; Kanal 4, 10, 16" 
'<Region> "Modul 4 Kanal 4" Beschleunigungssensor
  Par_44 = P2_ADC24(AIn_Modulnummer_1,4)
  'Abfrage mit 24 Bit, Modul liest mit 18 Bit, daher Rechtsverschiebung (Bitshift) um 6 Stellen
  Par_44 = Shift_Right(Par_44,6)
  Kanal_4_04 = Par_44
  'Umrechnung des Spannungswerts
  FPar_44 = (20*(Kanal_4_04/2^18)-9.992) 
  Kanal_4_04 = FPar_44
  Data_144 = Kanal_4_04
  'Umrechnung von g in m/s^2
  FPar_45 = FPar_44/0.01618          
  Beschleunigung = FPar_45
  Data_145 = Beschleunigung
'<Endregion>
    
'<Region> "Modul 4 Kanal 10" Drucksensor
  Par_41 = P2_ADC24(AIn_Modulnummer_1,10)
  'Abfrage mit 24 Bit, Modul liest mit 18 Bit, daher Rechtsverschiebung (Bitshift) um 6 Stellen
  Par_41 = Shift_Right(Par_41,6)
  Kanal_4_10 = Par_41
  FPar_41 = 20*(Kanal_4_10/2^18)-10 
  Kanal_4_10 = FPar_42
  'Data_141 = Kanal_4_10
  'Druckpolynom
  FPar_42 = 7.419605321320829e-06 * FPar_41^4 + 1.151875980614826e-04 * FPar_41^3 -0.003608840831045 * FPar_41^2 + 10.036314651348565 * FPar_41 -0.090362785744654 
  Druck = FPar_42
  Data_141 = Druck
'<Endregion>

'<Region> "Modul 4 Kanal 16" Abstandssensor
  Par_56 = P2_ADC24(AIn_Modulnummer_1,16)
  'Abfrage mit 24 Bit, Modul liest mit 16 Bit, daher Rechtsverschiebung (Bitshift) um 6 Stellen
  Par_56 = Shift_Right(Par_56,8)
  Kanal_4_16 = Par_56
  FPar_56 = 20*(Kanal_4_16/2^16)-10 -0.173 '1 Volt entspricht 1m / 0,1V entspricht 10cm
  Kanal_4_16 = FPar_56 
  Data_156 = Kanal_4_16
'<Endregion>

  
  t1 = t
  t = FPar_40
 
  'Velocity from Acceleration
  acc1 = acc
  acc = FPar_45
  velocity_a = ((acc-acc1)*(t1-t)) 
  FPar_51 = velocity_a
  Data_151 = FPar_51
  
  'Velocity from Height
  h1 = h
  h = FPar_56
  velocity = ((h-h1)/(t1-t)) 
  FPar_52 = velocity
  Data_152 = FPar_52
  
  'Acceleration from Height
  acceleration_h = a + ((h-h1)/(t1-t)^2) 
  FPar_53 =  acceleration_h
  Data_153 = FPar_53
  
  'Height from Acceleration 
  altitude_acc = h0 + 0.5*((acc-acc1)*(t1-t)^2)  
  FPar_50 =  acceleration_h
  Data_150 = FPar_50
