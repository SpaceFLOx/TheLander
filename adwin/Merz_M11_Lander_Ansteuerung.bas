'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
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
' Foldings                       = 273
'<Header End>
#Include ADwinPro_All.Inc
Import Math.lib   

Dim Abtastfrequenz_Hz_TRA_Anst as Float

'TRA-Out Modul 1 RackPos 2
Dim TRA_Out_Modulnummer_1 as Integer

'<Region> "Datenfelder Output"
Dim Data_120[500003] as Float as fifo  'Datenfeld Zeit
Dim Data_121[500003] as Float as fifo  'Datenfeld ATV-1
Dim Data_122[500003] as Float as fifo  'Datenfeld ATV-2
Dim Data_123[500003] as Float as fifo  'Datenfeld kommandierte Höhe
Dim Data_124[500003] as Float as fifo  'Datenfeld Control_U
Dim Data_125[500003] as Float as fifo  'Datenfeld Error
Dim Data_126[500003] as Float as fifo  'Datenfeld Derivative
Dim Data_127[500003] as Float as fifo  'Datenfeld Integral
Dim Data_128[500003] as Float as fifo  
Dim Data_129[500003] as Float as fifo  
Dim Data_130[500003] as Float as fifo  
Dim Data_131[500003] as Float as fifo  
Dim Data_132[500003] as Float as fifo
Dim Data_133[500003] as Float as fifo  
Dim Data_134[500003] as Float as fifo  
Dim Data_135[500003] as Float as fifo
Dim Data_136[500003] as Float as fifo
Dim Data_137[500003] as Float as fifo
Dim Data_138[500003] as Float as fifo
Dim Data_139[500003] as Float as fifo
'<Endregion>

Dim i as Integer

'Ansteuerungskanäle (1-16) TRA-Modul 1
'<Region> "TRA1"
Dim TRA_Out_1_01 as Integer
Dim TRA_Out_1_02 as Integer
Dim TRA_Out_1_03 as Integer
'<Endregion>

'<Region> "ATV1"
Dim force_off as Integer
Dim w as Float
Dim w1 as Float
Dim v as Float
Dim v1 as Float
Dim t_ein_v1 as Float
Dim t_aus_v1 as Float
Dim t_ein_v2 as Float
Dim t_aus_v2 as Float
Dim t_sample as Float
Dim t_on_atv1 as Float
Dim t_on_atv2 as Float
Dim t_off_atv1 as Float
Dim t_off_atv2 as Float
Dim y as Float
Dim t_ein as Float
Dim pi as Float

Dim time as Float
Dim next_time as Float

Dim hc as Float
Dim hm as Float
Dim pwm_time as Float
Dim ts as Float
Dim control_u as Float
Dim kp as Float
Dim ki as Float
Dim kd as Float
Dim error as Float
Dim error_last as Float
Dim new_integral_error as Float
Dim integral_error as Float
Dim derivative_error as Float
Dim max_pid_output as Float
Dim min_pid_output as Float
Dim on_time as Float
Dim cycle_time as Float
Dim duty_cycle as Float
Dim max_output as Float
Dim u_output as Float
'<Endregion>

Init:

  'Processdelay = 300000
  Processdelay = 3750000
  
  Abtastfrequenz_Hz_TRA_Anst = 1/(ProcessDelay*3.333333333333333333333*1e-9)
  
  TRA_Out_Modulnummer_1 = 2   'RackPos TRA-Modul 1

'<Region> "Fifo Clear"
  Fifo_clear(120) Zeit-Parameter
  Fifo_clear(121)
  Fifo_clear(122)
  Fifo_clear(123)
  Fifo_clear(124)
  Fifo_clear(125)
  Fifo_clear(126)
  Fifo_clear(127)
  Fifo_clear(128)
  Fifo_clear(129)
  Fifo_clear(130)
  Fifo_clear(131)
  Fifo_clear(132)
  Fifo_clear(133)
  Fifo_clear(134)
  Fifo_clear(135)
  Fifo_clear(136)
  Fifo_clear(137)
  Fifo_clear(138)
  Fifo_clear(139)
'<Endregion>

  pi = 3.1415926
  t_ein = 0
  
  next_time = 0
  ts = 0.0125
  error = 0
  error_last = 0
  integral_error = 0
  u_output = 0
  duty_cycle = 0.05
  min_pid_output = 0
  max_pid_output = 10
  max_output = 10
  
  
  
  
Event:

  'LED der Module anschalten
  P2_Set_LED(TRA_Out_Modulnummer_1,1)
 
  'Zeitstempel berechnen/ schreiben
  FPar_20 = FPar_1
  Data_120 = FPar_20 
  
  t_sample = 1/Abtastfrequenz_Hz_TRA_Anst
  time = FPar_20
  
  if (Par_37 = 0) then
    FPar_30 = Par_30/100
  else
    FPar_30 = (0.60 * sin(0.4*t_ein))+1
    t_ein = t_ein + t_sample
  endif
  
  if (Par_35 = 0) then  
    if ((Par_38 = 0) and (Par_36 = 0)) then
      
      Par_22 = Par_21 'ATV1 wie Slider in UI
      Par_25 = atv1(Par_22, FPar_21, FPar_22) 'Pulse ATV1 = Slider_On Par_22, t_on FPar_21, t_off FPar_22
      Par_24 = Par_23 'ATV2 wie Slider in UI
      Par_26 = atv2(Par_24, FPar_23, FPar_24) 'Pulse ATV2 = Slider_On Par_24, t_on FPar_23, t_off FPar_24
      
    else
      Par_22 = 0
      Par_24 = 0
      Par_26 = Par_25
    endif
    
  else
    if (time >= next_time) then
      hc = FPar_30
      kp = FPar_31
      ki = FPar_32
      kd = FPar_33
          
      pwm_time = FPar_20
      hm = FPar_56
          
      error = hc - hm
      new_integral_error = integral_error + error * ts
      derivative_error = (error - error_last) / ts
      control_u = kp * error + ki * new_integral_error + kd * derivative_error
          
      if (control_u > max_pid_output) then
        control_u = max_pid_output
        new_integral_error = integral_error
      else
        if (control_u < min_pid_output) then
          control_u = min_pid_output
          new_integral_error = integral_error
        else
          control_u = control_u
          integral_error = new_integral_error
        endif
      endif
          
      error_last = error
          
      on_time = (control_u/max_output * duty_cycle)*1000
      cycle_time = Mod(FPar_20*1000, duty_cycle*1000)
      FPar_28 = cycle_time
      FPar_27 = on_time
      if (cycle_time < on_time) then
        u_output = 1
      else
        u_output = 0
      endif
          
      Par_25 = u_output
      Par_26 = Par_25
      
      FPar_36 = error
      FPar_37 = new_integral_error
      FPar_38 = derivative_error
      FPar_39 = control_u
      
      next_time = time + ts
      FPar_26 = next_time
    else
      u_output = u_output
      Par_25 = u_output
      Par_26 = Par_25
    endif
    
    
      
  endif

Function atv1(on, t_on, t_off) As Float
  t_on_atv1 = t_on
  t_off_atv1 = t_off
   
  if (on <= 0) then
    if (t_ein_v1 = 0) then
      atv1 = 0
      t_ein_v1 = 0
      t_aus_v1 = t_aus_v1 + t_sample
    else
      if (t_ein_v1 < t_on_atv1) then
        atv1 = 1
        t_ein_v1 = t_ein_v1 + t_sample
        t_aus_v1 = 0
      else
        atv1 = 0
        t_ein_v1 = 0
        t_aus_v1 = t_aus_v1 + t_sample
      endif
    endif
  else
    if (t_ein_v1 < t_on_atv1) then
      if (t_aus_v1 = 0) then
        atv1 = 1
        t_ein_v1 = t_ein_v1 + t_sample
        t_aus_v1 = 0
      else
        if (t_aus_v1 < t_off_atv1) then 'hier könnte es Probleme machen
          atv1 = 0
          t_ein_v1 = 0
          t_aus_v1 = t_aus_v1 + t_sample
        else
          atv1 = 1
          t_ein_v1 = t_ein_v1 + t_sample
          t_aus_v1 = 0
        endif
      endif
    else
      atv1 = 0
      t_ein_v1 = 0
      t_aus_v1 = t_aus_v1 + t_sample
    endif      
  endif 

EndFunction
  
Function atv2(on, t_on, t_off) As Float 
  t_on_atv2 = t_on
  t_off_atv2 = t_off 
      
  if (on <= 0) then
    if (t_ein_v2 = 0) then
      atv2 = 0
      t_ein_v2 = 0
      t_aus_v2 = t_aus_v2 + t_sample
    else
      if (t_ein_v2 < t_on_atv2) then
        atv2 = 1
        t_ein_v2 = t_ein_v2 + t_sample
        t_aus_v2 = 0
      else
        atv2 = 0
        t_ein_v2 = 0
        t_aus_v2 = t_aus_v2 + t_sample
      endif
    endif
  else
    if (t_ein_v2 < t_on_atv2) then
      if (t_aus_v2 = 0) then
        atv2 = 1
        t_ein_v2 = t_ein_v2 + t_sample
        t_aus_v2 = 0
      else
        if (t_aus_v2 < t_off_atv2) then 'hier könnte es Probleme machen
          atv2 = 0
          t_ein_v2 = 0
          t_aus_v2 = t_aus_v2 + t_sample
        else
          atv2 = 1
          t_ein_v2 = t_ein_v2 + t_sample
          t_aus_v2 = 0
        endif
      endif
    else
      atv2 = 0
      t_ein_v2 = 0
      t_aus_v2 = t_aus_v2 + t_sample
    endif      
  endif
EndFunction

Data_121 = Par_25  'Pulse ATV1   
Data_122 = Par_26  'Pulse ATV2 
Data_130 = FPar_30 'kommandierte Höhe
Data_131 = FPar_31 'P-Gain
Data_132 = FPar_32 'D-Gain
Data_133 = FPar_33 'I-Gain
Data_134 = FPar_34 'N-Gain
Data_135 = FPar_35 'Omega_Abtastrate
Data_136 = FPar_36 'error
Data_137 = FPar_37 'integral
Data_138 = FPar_38 'derivative
Data_139 = FPar_39 'control_u

'<Region> "TRA Modul 1"
TRA_Out_1_01 = Par_25     'ATV1
TRA_Out_1_02 = Par_26     'ATV2
TRA_Out_1_03 = Par_39     'EMagnet
'<Endregion>

P2_Digout(TRA_Out_Modulnummer_1, 0, TRA_Out_1_01)    'ATV1
P2_Digout(TRA_Out_Modulnummer_1, 1, TRA_Out_1_02)    'ATV2
P2_Digout(TRA_Out_Modulnummer_1, 2, TRA_Out_1_03)    'E-Magnet
