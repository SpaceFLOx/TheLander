'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 6
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

Dim Zeit_Temp as Float
Dim Abtastfrequenz_Hz_Temp as Float

'TC Modul 1 RackPos 6
Dim TC_Modulnummer_1 as Integer

'<Region> "Datenfeld Zeit"
Dim Data_160[500003] as Float as fifo
'<Endregion>

'<Region> "Datenfelder Arrays Fifos, Thermomodul 8 Eing?nge"
Dim Data_161[500003] as Float as fifo
'Dim Data_162[500003] as Float as fifo
'Dim Data_163[500003] as Float as fifo
'Dim Data_164[500003] as Float as fifo
'Dim Data_165[500003] as Float as fifo
'Dim Data_166[500003] as Float as fifo
'Dim Data_167[500003] as Float as fifo
'Dim Data_168[500003] as Float as fifo
'<Endregion>
Init:
  
  Processdelay = 3000000
  
  'RackPos des Moduls
  TC_Modulnummer_1 = 6
  
  'Abtastrate Thermo ADwin S. 216
  P2_TC_Set_Rate(TC_Modulnummer_1,6) '6 = 110 Hz,
  
'<Region> Zeit-Parameter Temperaturen
  Fifo_clear(160)
'<Endregion>
  
'<Region> "Modul 1"
  Fifo_clear(161)
  '  Fifo_clear(162)
  '  Fifo_clear(163)
  '  Fifo_clear(164)
  '  Fifo_clear(165)
  '  Fifo_clear(166)
  '  Fifo_clear(167)
  '  Fifo_clear(168)
'<Endregion>

Event:
  
  'Abfrage der Eing?nge
  P2_TC_Latch(TC_Modulnummer_1)
  
  'LED der Module anschalten
  if (Par_2 >= 1) then
    P2_Set_LED(TC_Modulnummer_1-1,1)
  else
    P2_Set_LED(TC_Modulnummer_1-1,0)
  endif
  
'<Region> Zeit-Parameter Temperaturen
  FPar_60 = FPar_1
  Data_160 = FPar_60
'<Endregion>
  
'<Region> "Modul1" 
  'Holt den Wert von Modul 6, Thermo 1, Typ K, in ?C und gibt den Wert als FloatingParameter aus
  FPar_61 = P2_TC_Read_Latch(TC_Modulnummer_1,1,1,1)    'T_Ref
  '  FPar_62 = P2_TC_Read_Latch(TC_Modulnummer_1,2,1,1)    
  '  FPar_63 = P2_TC_Read_Latch(TC_Modulnummer_1,3,1,1)    
  '  FPar_64 = P2_TC_Read_Latch(TC_Modulnummer_1,4,1,1)    
  '  FPar_65 = P2_TC_Read_Latch(TC_Modulnummer_1,5,1,1)
  '  FPar_66 = P2_TC_Read_Latch(TC_Modulnummer_1,6,1,1)
  '  FPar_67 = P2_TC_Read_Latch(TC_Modulnummer_1,7,1,1)
  '  FPar_68 = P2_TC_Read_Latch(TC_Modulnummer_1,8,1,1)
'<Endregion> 

'<Region> "Modul1" 
  'Schreibt den Wert von Thermo xy in den n?chsten freien Speicher des fifo
  Data_161 = FPar_61
  '  Data_162 = FPar_62
  '  Data_163 = FPar_63
  '  Data_164 = FPar_64
  '  Data_165 = FPar_65
  '  Data_166 = FPar_66
  '  Data_167 = FPar_67
  '  Data_168 = FPar_68
'<Endregion>
