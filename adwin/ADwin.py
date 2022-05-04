# -*- coding: cp1252 -*-
''' Collection of subroutines for the control of the ADwin measurement data acquisition '''


#   Copyright 2017 - 2019 J�ger Computergesteuerte Messtechnik GmbH
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import ctypes
import sys
import array
import struct
if sys.platform == 'win32':
    if sys.version_info[0] == 3:
        import winreg as _winreg
    else:
        import _winreg


# ADwin-Exception
class ADwinError(Exception):
    def __init__(self, functionName, errorText, errorNumber):
        self.functionName = functionName
        self.errorText = errorText
        self.errorNumber = errorNumber

    def __str__(self):
        if sys.version_info[0] == 3:
            return 'Function %s, errorNumber %d: %s' % (self.functionName, self.errorNumber, self.errorText)
        else:
            return 'Function ' + self.functionName + ', errorNumber ' + str(self.errorNumber) + ': ' + str(self.errorText)


class ADwin:
    __err = ctypes.c_int32(0)
    __errPointer = ctypes.pointer(__err)
    ADWIN_DATATYPE_INT8 = 1
    ADWIN_DATATYPE_INT16 = 2
    ADWIN_DATATYPE_INT32 = 3
    ADWIN_DATATYPE_SINGLE = 5
    ADWIN_DATATYPE_DOUBLE = 6
    ADWIN_DATATYPE_INT64 = 7
    ADwin_Datatypes = ("undefined", "byte", "short", "int32", "long", "float32", "float64", "int64", "string")
    Processor_Types = {2:"T2", 4:"T4", 5:"T5", 8:"T8", 9:"T9", 1010:"T10", 1011:"T11", 1012:"T12", 10121:"T12.1"}

    def __init__(self, DeviceNo=1, raiseExceptions=1):
        self.version = '0.16.3'

        if sys.platform.startswith('linux'):
            try:
                if sys.version_info[0] == 3:
                    f = open('/etc/adwin/ADWINDIR', 'r')
                else:
                    f = file('/etc/adwin/ADWINDIR', 'r')
                self.ADwindir = f.readline()[:-1] + '/'  # without newline at the end
                self.dll = ctypes.CDLL(self.ADwindir + 'lib/libadwin.so')
            except:
                raise ADwinError('__init__', 'shared library libadwin.so not found.', 200)
            f.close()
            self.dll.Set_DeviceNo(DeviceNo)
        elif sys.platform == 'darwin':
            try:
                if sys.version_info[0] == 3:
                    f = open('/etc/adwin/ADWINDIR', 'r')
                else:
                    f = file('/etc/adwin/ADWINDIR', 'r')
                self.ADwindir = f.readline()[:-1] + '/'  # without newline at the end
                self.dll = ctypes.CDLL('/Library/Frameworks/adwin32.framework/Versions/A/libadwin.5.dylib')
                self.dll.Set_DeviceNo(DeviceNo)
            except:
                raise ADwinError('__init__', 'shared library libadwin.5.dylib not found.', 200)
        else:
            self.ADWIN_DATATYPE_INT32 = 2
            try:
                aKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"SOFTWARE\J�ger Me�technik GmbH\ADwin\Directory")
                self.ADwindir = str(_winreg.QueryValueEx(aKey, 'BTL')[0])
                _winreg.CloseKey(aKey)
            except:
                try:
                    aKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\J�ger Me�technik GmbH\ADwin\Directory")
                    self.ADwindir = str(_winreg.QueryValueEx(aKey, 'BTL')[0])
                    _winreg.CloseKey(aKey)
                except:
                    try:
                        aKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\ADwin\Directory")
                        self.ADwindir = str(_winreg.QueryValueEx(aKey, 'BTL')[0])
                        _winreg.CloseKey(aKey)
                    except:
                        raise ADwinError('__init__', 'Could not read Registry.', 200)
            try:
                if struct.calcsize("P") == 4:
                    self.dll = ctypes.WinDLL('c:\\windows\\adwin32.dll')
                else:
                    self.dll = ctypes.WinDLL('c:\\windows\\adwin64.dll')
                self.dll.DeviceNo = DeviceNo
            except:
                raise ADwinError('__init__', 'ADwin-DLL not found.', 200)
        self.raiseExceptions = raiseExceptions
        self.DeviceNo = DeviceNo

    def __checkError(self, functionName):
        if self.__err.value != 0:
            if self.raiseExceptions != 0:
                raise ADwinError(functionName, self.Get_Error_Text(self.__err.value), self.__err.value)

    # system control and system information
    def Boot(self, Filename):
        '''Boot initializes the ADwin system and loads the file of the \
            operating system.'''
        if sys.version_info[0] == 3:
            self.dll.e_ADboot(Filename.encode(), self.DeviceNo, 100000, 0, self.__errPointer)
        else:
            self.dll.e_ADboot(Filename, self.DeviceNo, 100000, 0, self.__errPointer)
        self.__checkError('Boot')

    def Test_Version(self):
        '''Test_Version checks, if the correct operating system for the
            processor has been loaded and if the processor can be accessed.'''
        self.dll.e_ADTest_Version.restype = ctypes.c_short
        ret = self.dll.e_ADTest_Version(self.DeviceNo, 0, self.__errPointer)
        return ret

    def Processor_Type(self):
        '''Processor_Type returns the processor type of the system.'''
        ret = self.dll.e_ADProzessorTyp(self.DeviceNo, self.__errPointer)
        self.__checkError('Processor_Type')
        if ret == 1000:
            ret = 9
        return self.Processor_Types.get(ret, "unknown")

    def Workload(self):
        '''Workload returns the processor workload.'''
        self.dll.e_AD_Workload.restype = ctypes.c_short
        ret = self.dll.e_AD_Workload(0, self.DeviceNo, self.__errPointer)
        self.__checkError('Workload')
        return ret

    def Free_Mem(self, Mem_Spec):
        '''Free_Mem determines the free memory for the different memory types.'''
        ret = self.dll.e_AD_Memory_all_byte(Mem_Spec, self.DeviceNo, self.__errPointer)
        self.__checkError('Free_Mem')
        return ret

    # Process control
    def Load_Process(self, Filename):
        '''Load_Process loads the binary file of a process into the ADwin system.'''
        if sys.version_info[0] == 3:
            self.dll.e_ADBload(Filename.encode(), self.DeviceNo, 0, self.__errPointer)
        else:
            self.dll.e_ADBload(Filename, self.DeviceNo, 0, self.__errPointer)
        self.__checkError('Load_Process')

    def Start_Process(self, ProcessNo):
        '''Start_Process starts a process.'''
        self.dll.e_ADB_Start(ProcessNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Start_Process')

    def Stop_Process(self, ProcessNo):
        '''Stop_Process stops a process.'''
        self.dll.e_ADB_Stop(ProcessNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Stop_Process')

    def Clear_Process(self, ProcessNo):
        '''Clear_Process deletes a process from memory.'''
        self.dll.e_Clear_Process(ProcessNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Clear_Process')

    def Process_Status(self, ProcessNo):
        '''Process_Status returns the status of a process.'''
        ret = self.dll.e_Get_ADBPar(-100 + ProcessNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Process_Status')
        return ret

    def Get_Processdelay(self, ProcessNo):
        '''Get_Processdelay returns the parameter Processdelay for a process.'''
        ret = self.dll.e_Get_ADBPar(-90 + ProcessNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_Processdelay')
        return ret

    def Set_Processdelay(self, ProcessNo, Processdelay):
        '''Set_Processdelay sets the parameter Globaldelay for a process.'''
        self.dll.e_Set_ADBPar(-90 + ProcessNo, Processdelay, self.DeviceNo, self.__errPointer)
        self.__checkError('Set_Processdelay')

    # Transfer of global variables
    def Set_Par(self, Index, Value):
        '''Set_Par sets a global long variable to the specified value.'''
        self.dll.e_Set_ADBPar(Index, Value, self.DeviceNo, self.__errPointer)
        self.__checkError('Set_Par')

    def Get_Par(self, no):
        '''Get_Par returns the value of a global long variable.'''
        ret = self.dll.e_Get_ADBPar(no, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_Par')
        return ret

    def Get_Par_Block(self, StartIndex, Count):
        '''Get_Par_Block returns a number of global long variables, which is to be indicated.'''
        dataType = ctypes.c_int32 * Count
        data = dataType(0)
        self.dll.e_Get_ADBPar_All(StartIndex, Count, data, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_Par_Block')
        return data

    def Get_Par_All(self):
        '''Get_Par_All returns all global long variables.'''
        dataType = ctypes.c_int32 * 80
        data = dataType(0)
        self.dll.e_Get_ADBPar_All(1, 80, data, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_Par_All')
        return data

    def Set_FPar(self, Index, Value):
        '''Set_FPar sets a global float variable to a specified value.'''
        _val = ctypes.c_float(Value)
        self.dll.e_Set_ADBFPar(Index, _val, self.DeviceNo, self.__errPointer)
        self.__checkError('Set_FPar')

    def Get_FPar(self, Index):
        '''Get_FPar returns the value of a global float variable.'''
        self.dll.e_Get_ADBFPar.restype = ctypes.c_float
        ret = self.dll.e_Get_ADBFPar(Index, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_FPar')
        return ret

    def Set_FPar_Double(self, Index, Value):
        '''Set_FPar_Double sets a global double variable to a specified value.'''
        _val = ctypes.c_double(Value)
        self.dll.e_Set_ADBFPar_Double(Index, _val, self.DeviceNo, self.__errPointer)
        self.__checkError('Set_FPar_Double')

    def Get_FPar_Double(self, Index):
        '''Get_FPar returns the value of a global double variable.'''
        self.dll.e_Get_ADBFPar_Double.restype = ctypes.c_double
        ret = self.dll.e_Get_ADBFPar_Double(Index, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_FPar_Double')
        return ret

    def Get_FPar_Block(self, StartIndex, Count):
        '''Get_FPar_Block returns a number of global float variables, which is to be indicated.'''
        dataType = ctypes.c_float * Count
        data = dataType(0)
        self.dll.e_Get_ADBFPar_All(StartIndex, Count, data, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_FPar_Block')
        return data

    def Get_FPar_Block_Double(self, StartIndex, Count):
        '''Get_FPar_Block_Double returns a number of global double variables, which is to be indicated.'''
        dataType = ctypes.c_double * Count
        data = dataType(0)
        self.dll.e_Get_ADBFPar_All_Double(StartIndex, Count, data, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_FPar_Block_Double')
        return data

    def Get_FPar_All(self):
        '''Get_Par_All returns all global float variables.'''
        dataType = ctypes.c_float * 80
        data = dataType(0)
        self.dll.e_Get_ADBFPar_All(1, 80, data, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_FPar_All')
        return data

    def Get_FPar_All_Double(self):
        '''Get_Par_All_Double returns all global double variables.'''
        dataType = ctypes.c_double * 80
        data = dataType(0)
        self.dll.e_Get_ADBFPar_All_Double(1, 80, data, self.DeviceNo, self.__errPointer)
        self.__checkError('Get_FPar_All_Double')
        return data

    # Transfer of data arrays
    def Data_Length(self, Data_No):
        '''Data_Length returns the length of an array, declared under ADbasic, that means the number of elements.'''
        ret = self.dll.e_GetDataLength(Data_No, self.DeviceNo, self.__errPointer)
        self.__checkError('Data_Length')
        return ret

    def Data_Type(self, Data_No):
        '''Returns a tupel (number, string) of the type of a data'''
        if (Data_No < 1) or (Data_No > 200):
            return 0, "undefined"
        if sys.platform == 'win32':
            self.dll.e_GetDataTyp.restype = ctypes.c_short
            ret = self.dll.e_GetDataTyp(Data_No, self.DeviceNo, self.__errPointer)
            self.__checkError('Data_Type')
        else:
            self.dll.adwin_get_data_type.restype = ctypes.c_short
            ret = self.dll.adwin_get_data_type(Data_No, self.DeviceNo)
        if ret == 3:
            if self.Processor_Type() == 1012:  # only return-type 3 is not clearly between different processors
                ret = 4
        if (ret >= 0) and (ret <= 8):
            return ret, self.ADwin_Datatypes[ret]
        else:
            return 0, "undefined"
    
    def SetData_Byte(self, Data, DataNo, Startindex, Count):
        '''SetData_Byte transfers short data from the PC into a DATA array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int8_Array
            dataType = ctypes.c_int8 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes-array
            data = Data
        self.dll.e_Set_Data(data, self.ADWIN_DATATYPE_INT8, DataNo, Startindex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_Byte')
    
    def GetData_Byte(self, DataNo, StartIndex, Count):
        '''GetData_Byte transfers int8 data from a DATA array of an ADwin system into an array.'''
        dataType = ctypes.c_int8 * Count
        data = dataType(0)
        self.dll.e_Get_Data(data, self.ADWIN_DATATYPE_INT8, DataNo, StartIndex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetData_Byte')
        return data
    
    def SetData_Short(self, Data, DataNo, Startindex, Count):
        '''SetData_Short transfers short data from the PC into a DATA array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int16_Array
            dataType = ctypes.c_int16 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes-array
            data = Data
        self.dll.e_Set_Data(data, self.ADWIN_DATATYPE_INT16, DataNo, Startindex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_Short')

    def GetData_Short(self, DataNo, StartIndex, Count):
        '''GetData_Short transfers int16 data from a DATA array of an ADwin system into an array.'''
        dataType = ctypes.c_int16 * Count
        data = dataType(0)
        self.dll.e_Get_Data(data, self.ADWIN_DATATYPE_INT16, DataNo, StartIndex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetData_Short')
        return data

    def SetData_Long(self, Data, DataNo, Startindex, Count):
        '''SetData_Long transfers long data from the PC into a DATA array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int32_Array
            dataType = ctypes.c_int32 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes-array
            data = Data
        self.dll.e_Set_Data(data, self.ADWIN_DATATYPE_INT32, DataNo, Startindex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_Long')

    def GetData_Long(self, DataNo, StartIndex, Count):
        '''GetData_Long transfers long data from a DATA array of an ADwin system into an array.'''
        dataType = ctypes.c_int32 * Count
        data = dataType(0)
        self.dll.e_Get_Data(data, self.ADWIN_DATATYPE_INT32, DataNo, StartIndex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetData_Long')
        return data

    def SetData_Float(self, Data, DataNo, Startindex, Count):
        '''SetData_Float transfers float data from the PC into a DATA array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_float_Array
            dataType = ctypes.c_float * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_float_Array
            data = Data
        self.dll.e_Set_Data(data, self.ADWIN_DATATYPE_SINGLE, DataNo, Startindex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_Float')

    def GetData_Float(self, DataNo, StartIndex, Count):
        '''GetData_Float transfers float data from a DATA array of an ADwin system into an array.'''
        dataType = ctypes.c_float * Count
        data = dataType(0)
        self.dll.e_Get_Data(data, self.ADWIN_DATATYPE_SINGLE, DataNo, StartIndex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetData_Float')
        return data

    def SetData_Double(self, Data, DataNo, Startindex, Count):
        '''SetData_Double transfers double data from the PC into a DATA array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_double_Array
            dataType = ctypes.c_double * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_double_Array
            data = Data
        self.dll.e_Set_Data(data, self.ADWIN_DATATYPE_DOUBLE, DataNo, Startindex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_Double')

    def GetData_Double(self, DataNo, StartIndex, Count):
        '''GetData_Double transfers double data from a DATA array of an ADwin system into an array.'''
        dataType = ctypes.c_double * Count
        data = dataType(0)
        self.dll.e_Get_Data(data, self.ADWIN_DATATYPE_DOUBLE, DataNo, StartIndex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetData_Double')
        return data

    def SetData_Int64(self, Data, DataNo, Startindex, Count):
        '''SetData_Double transfers int64 data from the PC into a DATA array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int64_Array
            dataType = ctypes.c_int64 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_int64_Array
            data = Data
        self.dll.e_Set_Data(data, self.ADWIN_DATATYPE_INT64, DataNo, Startindex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_Int64')
    
    def GetData_Int64(self, DataNo, StartIndex, Count):
        '''GetData_Double transfers int64 data from a DATA array of an ADwin system into an array.'''
        dataType = ctypes.c_int64 * Count
        data = dataType(0)
        self.dll.e_Get_Data(data, self.ADWIN_DATATYPE_INT64, DataNo, StartIndex, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetData_Int64')
        return data

    # Transfer of FIFO Arrays
    def Fifo_Empty(self, FifoNo):
        '''Fifo_Empty provides the number of free elements of a FIFO array.'''
        ret = self.dll.e_Get_Fifo_Empty(FifoNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Fifo_Empty')
        return ret

    def Fifo_Full(self, FifoNo):
        '''Fifo_Full provides the number of used elements of a FIFO array.'''
        ret = self.dll.e_Get_Fifo_Count(FifoNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Fifo_Full')
        return ret

    def Fifo_Clear(self, FifoNo):
        '''Fifo_Clear initializes the pointer for writing and reading a FIFO array.'''
        self.dll.e_Clear_Fifo(FifoNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Fifo_Clear')

    def SetFifo_Byte(self, FifoNo, Data, Count):
        '''SetFifo_Byte transfers byte data from the PC to a FIFO array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int8_Array
            dataType = ctypes.c_int8 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_int8_Array
            data = Data
        self.dll.e_Set_Fifo(data, self.ADWIN_DATATYPE_INT8, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetFifo_Byte')

    def GetFifo_Byte(self, FifoNo, Count):
        '''GetFifo_Byte transfers byte FIFO data from the ADwin system to the PC.'''
        dataType = ctypes.c_int8 * Count
        data = dataType(0)
        self.dll.e_Get_Fifo(data, self.ADWIN_DATATYPE_INT8, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetFifo_Byte')
        return data
    
    def SetFifo_Short(self, FifoNo, Data, Count):
        '''SetFifo_Short transfers short data from the PC to a FIFO array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int16_Array
            dataType = ctypes.c_int16 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_int16_Array
            data = Data
        self.dll.e_Set_Fifo(data, self.ADWIN_DATATYPE_INT16, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetFifo_Short')

    def GetFifo_Short(self, FifoNo, Count):
        '''GetFifo_Short transfers short FIFO data from the ADwin system to the PC.'''
        dataType = ctypes.c_int16 * Count
        data = dataType(0)
        self.dll.e_Get_Fifo(data, self.ADWIN_DATATYPE_INT16, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetFifo_Short')
        return data
    
    def SetFifo_Long(self, FifoNo, Data, Count):
        '''SetFifo_Long transfers long data from the PC to a FIFO array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_int32_Array
            dataType = ctypes.c_int32 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_int32_Array
            data = Data
        self.dll.e_Set_Fifo(data, self.ADWIN_DATATYPE_INT32, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetFifo_Long')

    def GetFifo_Long(self, FifoNo, Count):
        '''GetFifo_Long transfers long FIFO data from the ADwin system to the PC.'''
        dataType = ctypes.c_int32 * Count
        data = dataType(0)
        self.dll.e_Get_Fifo(data, self.ADWIN_DATATYPE_INT32, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetFifo_Long')
        return data

    def SetFifo_Float(self, FifoNo, Data, Count):
        '''SetFifo_Float transfers float data from the PC into a FIFO array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_float_Array
            dataType = ctypes.c_float * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_float_Array
            data = Data
        self.dll.e_Set_Fifo(data, self.ADWIN_DATATYPE_SINGLE, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetFifo_Float')

    def GetFifo_Float(self, FifoNo, Count):
        '''GetFifo_Float transfers float FIFO data from the ADwin system to the PC.'''
        dataType = ctypes.c_float * Count
        data = dataType(0)
        self.dll.e_Get_Fifo(data, self.ADWIN_DATATYPE_SINGLE, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetFifo_Float')
        return data

    def SetFifo_Double(self, FifoNo, Data, Count):
        '''SetFifo_Double transfers double data from the PC into a FIFO array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_double_Array
            dataType = ctypes.c_double * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_double_Array
            data = Data
        self.dll.e_Set_Fifo(data, self.ADWIN_DATATYPE_DOUBLE, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetFifo_Double')

    def GetFifo_Double(self, FifoNo, Count):
        '''GetFifo_Double transfers double FIFO data from the ADwin system to the PC.'''
        dataType = ctypes.c_double * Count
        data = dataType(0)
        self.dll.e_Get_Fifo(data, self.ADWIN_DATATYPE_DOUBLE, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetFifo_Double')
        return data
    
    def SetFifo_Int64(self, FifoNo, Data, Count):
        '''SetFifo_Int64 transfers int64 data from the PC into a FIFO array of the ADwin system.'''
        if (type(Data) == list) or (type(Data) == array.array):
            # convert list to ctypes.c_double_Array
            dataType = ctypes.c_int64 * Count
            data = dataType(0)
            for i in range(Count):
                data[i] = Data[i]
        else:  # ctypes.c_int64_Array
            data = Data
        self.dll.e_Set_Fifo(data, self.ADWIN_DATATYPE_INT64, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('SetFifo_Int64')

    def GetFifo_Int64(self, FifoNo, Count):
        '''GetFifo_Double transfers int64 FIFO data from the ADwin system to the PC.'''
        dataType = ctypes.c_int64 * Count
        data = dataType(0)
        self.dll.e_Get_Fifo(data, self.ADWIN_DATATYPE_INT64, FifoNo, Count, self.DeviceNo, self.__errPointer)
        self.__checkError('GetFifo_Int64')
        return data

    def Data2File(self, Filename, DataNo, StartIndex, Count, Mode):
        ''' Writes array-elements of ADwin-System immediately to harddisk '''
        if sys.version_info[0] == 3:
            self.dll.e_SaveFast(Filename.encode(), DataNo, StartIndex, Count, Mode, self.DeviceNo, self.__errPointer)
        else:
            self.dll.e_SaveFast(Filename, DataNo, StartIndex, Count, Mode, self.DeviceNo, self.__errPointer)
        self.__checkError('Data2File')

    def File2Data(self, Filename, DataType, DataNo, Startindex):
        ''' Writes a file immediately from harddisk to array-elements of ADwin-System '''
        # Hint: DataType constant
        #  2 = int32
        #  5 = float (32bit)
        #  6 = double (64bit)
        if sys.version_info[0] == 3:
            self.__err.value = self.dll.File2Data(Filename.encode(), DataType, DataNo, Startindex, self.DeviceNo)
        else:
            self.__err.value = self.dll.File2Data(Filename, DataType, DataNo, Startindex, self.DeviceNo)
        self.__checkError('File2Data')

    # Data arrays with string data
    def String_Length(self, DataNo):
        '''String_Length transfers the length of a data string to a DATA array.'''
        ret = self.dll.e_Get_Data_String_Length(DataNo, self.DeviceNo, self.__errPointer)
        self.__checkError('String_Length')
        return ret

    def SetData_String(self, DataNo, String):
        '''transfers a string into a DATA array.'''
        if sys.version_info[0] == 3:
            self.dll.e_Set_Data_String(String.encode(), DataNo, self.DeviceNo, self.__errPointer)
        else:
            self.dll.e_Set_Data_String(String, DataNo, self.DeviceNo, self.__errPointer)
        self.__checkError('SetData_String')

    def GetData_String(self, DataNo, MaxCount):
        '''GetData_String transfers a string from a DATA array into a buffer.'''
        dataType = ctypes.c_char * (MaxCount + 2)
        if sys.version_info[0] == 3:
            data = dataType(0)
            self.dll.e_Get_Data_String(data, MaxCount + 1, DataNo, self.DeviceNo, self.__errPointer)
            self.__checkError('GetData_String')
            return data.value
        else:
            data = dataType(' ')
            self.dll.e_Get_Data_String(data, MaxCount + 1, DataNo, self.DeviceNo, self.__errPointer)
            self.__checkError('GetData_String')
            return data

    def Clear_Data(self, DataNo):
        '''Clear a data'''
        self.dll.Clear_Data(DataNo, self.DeviceNo, self.__errPointer)
        self.__checkError('Clear_Data')

    # Control and error handling
    def Get_Error_Text(self, ErrorNumber):
        '''Get_Error_Text returns an error text related to an error number.'''
        text = ctypes.create_string_buffer(256)
        pText = ctypes.byref(text)
        self.dll.ADGetErrorText(ErrorNumber, pText, 256)
        return text.value.decode('utf-8')

    def Get_Last_Error(self):
        '''Get_Last_Error returns the number of the last error.'''
        return self.__err.value

    # retry_counter
    def Get_Retry_Counter(self):
        if sys.platform == 'win32':
            return self.dll.GETRETRY()
        else:
            return self.dll.getRetryCounter()

    def Inc_Retry_Counter(self):
        self.dll.incRetryCounter()

    def Reset_Retry_Counter(self):
        self.dll.resetRetryCounter()

    def Get_Device_Retry_Counter(self, DevNo):
        if sys.platform == 'win32':
            return self.dll.GETRETRY_DEVICE(DevNo)
        else:
            return self.dll.getDeviceRetryCounter(DevNo)

    def Reset_Device_Retry_Counter(self):
        self.resetDeviceRetryCounter(self.DeviceNo,)

    # GD_Transsize
    def Set_GD_Transsize(self, transsize):
        '''Set UDP-packagesize, default 336, max 4000'''
        self.dll.e_Set_GD_Transsize(transsize, self.DeviceNo, self.__errPointer)
        self.__checkError('Set_GD_Transsize')

    def Get_GD_Transsize(self):
        ret = self.dll.e_Get_GD_Transsize(self.DeviceNo, self.__errPointer)
        self.__checkError('Get_GD_Transsize')
        return ret
