import numpy as np
import pyvisa 

'''This is the automatically control the oscilloscope, function generator, and source meter by using pyvisa. 
I basically used each equiptment DPO 4054, AFG 31022, K2400 respectively.'''

rm = pyvisa.RecourceManager()


def scope_connection():
    ip_address = '192.168.1.20'  # IP address of the equipment
    visa_address = f'TCPIP0::{ip_address}::inst0::INSTR'
    try:
        scope = rm.open_resource(visa_address)
        print(f"connected successfully: {scope.query('*IDN?')}")
    except pyvisa.VisaIOError:
        print(f"Can not find the equipment with this address {visa_address}.")
    return scope
  
def func_gen_connection():
    func_gen_visa = 'GPIB0::11::INSTR'
    try:
        func_gen = rm.open_resource('GPIB0::11::INSTR')
        print(f"connected successfully: {func_gen.query('*IDN?')}")
    except pyvisa.VisaIOError:
        print(f"Can not find the equipment with this address {func_gen_visa}.")
    return func_gen
  
def source_connection():
    k2400_address = 'ASRL3::INSTR'
    try:
        k2400 = rm.open_resource(k2400_address)
        print(f"connected successfully: {k2400.query('*IDN?')}")
    except pyvisa.VisaIOError:
        print(f"Can not find the equipment with this address {k2400_address}.")
    return k2400

def func_gen_setting(func_gen,frequency, voltage, low):
    func_gen.write('*RST')#func_gen setting reset
    func_gen.write('SOURce1:FUNCtion:SHAPe SQUare')
    func_gen.write('SOURce2:FUNCtion:SHAPe SQUare')
    #func_gen.write(f'SOURce1:PULSe:WIDTh {pulse_width}ns')
    #func_gen.write(f'SOURce2:PULSe:WIDTh {pulse_width}ns')
    func_gen.write(f'SOURce1:FREQUENCY {frequency}')
    func_gen.write(f'SOURce2:FREQUENCY {frequency}')
    if voltage > 0:
        func_gen.write(f'SOURce1:VOLTage:LEVel:IMMediate:High {voltage}')
        func_gen.write(f'SOURce1:VOLTage:LEVel:IMMediate:Low {low}')
        func_gen.write(f'SOURce2:VOLTage:LEVel:IMMediate:High {voltage}')
        func_gen.write(f'SOURce2:VOLTage:LEVel:IMMediate:Low {low}')
    else:
        func_gen.write(f'SOURce1:VOLTage:LEVel:IMMediate:High {low}')
        func_gen.write(f'SOURce1:VOLTage:LEVel:IMMediate:Low {voltage}')
        func_gen.write(f'SOURce2:VOLTage:LEVel:IMMediate:High {low}')
        func_gen.write(f'SOURce2:VOLTage:LEVel:IMMediate:Low {voltage}')

  def scope_setting(scope, pulse_width, voltage,low):
    data = 50000
    scope.write('ACQUIRE:STATE OFF')
    scope.write('SELECT:CH1 ON')
    #scope.write('INPUT:IMPEDANCE CH1, 50')
    scope.write('SELECT:CH2 ON')
    #scope.write('INPUT:IMPEDANCE CH2, 50')
    scope.write('ACQUIRE:MODE SAMPLE')
    #scope.write('HORizontal:SAMPLERate 1E9')
    scope.write(f'HORizontal:RECOrdlength {data}')
    scope.write(f'HORIZONTAL:SCALE {pulse_width/2}')
    #scope.write('HORIZONTAL:SCALE 1E-6')
    scope.write('DATA:START 1')
    scope.write(f'DATA:STOP {data}')  # 총 몇개 point를 얻을 것인지

    '''샘플링 속도랑 메로리 깊이가 중요한게, 이걸로 인해서 취득하는 포인트 사이의 시간 간격이 나옴'''

    scope.write(f'CH1:SCALE 1')
    scope.write(f'CH2:SCALE 2')
    #scope.write('ACQUIRE:STOPAFTER SEQUENCE')
    #scope.write('AUTOSet')
    scope.write('ACQUIRE:STATE ON')
    # 트리거 유형을 '엣지'로 설정
    scope.write('TRIGGER:A:TYPE EDGE')
    # 트리거 소스 설정 (예: 채널 1)
    scope.write('TRIGGER:A:EDGE:SOURCE CH1')
    scope.write('TRIGGER:A:EDGE:SOURCE CH2')
    # Trigger rise slope
    scope.write('TRIGGER:A:EDGE:SLOPE Rise')
    # Trigger level
    scope.write(f'TRIGGER:A:LEVEL {low+999*(voltage-low)/1000}')

def scope_ascii_measure(scope):
    # Read data from CH1
    scope.write('DATA:SOURCE CH1')
    scope.write('DATa:ENCdg ASCII')  # Switch to ASCII encoding
    # Debugging: Print raw response to inspect its format
    raw_response = scope.query('CURVe?')
    # Assuming the numeric data starts after a specific character (e.g., a space or comma)
    numeric_data = raw_response[7:].split(' ')[-1]  # Modify this based on the actual format
    y1_ascii = np.array([float(val) for val in numeric_data.split(',')])
    # Retrieve scale factors for CH1
    y1mult = float(scope.query('WFMPRE:YMULT?').split()[-1])
    y1zero = float(scope.query('WFMPRE:YZERO?').split()[-1])
    y1off = float(scope.query('WFMPRE:YOFF?').split()[-1])
    # Process data for CH1 (apply scale factors)
    y1_processed = (y1_ascii - y1off) * y1mult + y1zero
    # Read data from CH2
    scope.write('DATA:SOURCE CH2')
    raw_response = scope.query('CURVe?')
    # Assuming the numeric data starts after a specific character (e.g., a space or comma)
    numeric_data = raw_response[7:].split(' ')[-1]  # Modify this based on the actual format
    y2_ascii = np.array([float(val) for val in numeric_data.split(',')])
    # Retrieve scale factors for CH2
    y2mult = float(scope.query('WFMPRE:YMULT?').split()[-1])
    y2zero = float(scope.query('WFMPRE:YZERO?').split()[-1])
    y2off = float(scope.query('WFMPRE:YOFF?').split()[-1])
    # Process data for CH2 (apply scale factors)
    y2_processed = (y2_ascii - y2off) * y2mult + y2zero
    # Calculate X increment (ensure the scope buffer size matches your data range)
    xincr = float(scope.query('WFMOutPRE:XINCR?').split()[-1])
    # Generate the X data based on the X increment and the number of data points
    x_data = np.arange(0, xincr * len(y1_processed), xincr)*1E6
    return [x_data, y1_processed/2, y2_processed/2]

def source_bias(k2400,voltage):
    k2400.write('*RST')  # 장비를 리셋
    k2400.write(':ROUT:TERM REAR')
    k2400.write(':SOUR:FUNC VOLT')  # 소스를 전압으로 설정
    k2400.write(':SOUR:VOLT:MODE FIX')  # 고정 전압 모드 설정
    k2400.write(':SENS:FUNC "CURR"')  # 측정 함수를 전류로 설정
    k2400.write(':SENS:CURR:PROT 1')  # 전류 측정 범위 설정 (예: 1A)
    k2400.write(f':SOUR:VOLT:LEV {voltage}')  # 전압 레벨을 2V로 설정
    k2400.write(':OUTP ON')  # 출력 활성화 (필요한 경우)

def scope_off(scope):
    scope.write('ACQuire:STATE OFF')
    scope.write('*RST')
    scope.close()

def func_gen_off(func_gen):
    func_gen.write('OUTPut1 OFF')  # 첫 번째 채널의 출력을 끔
    func_gen.write('OUTPut2 OFF')  # 두 번째 채널의 출력을 끔
    func_gen.close()

def source_off(k2400):
    k2400.write(':OUTP OFF')
    k2400.close()

