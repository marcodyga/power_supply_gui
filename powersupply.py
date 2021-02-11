import serial
import time

class PowerSupply:
    
    ser = False
    
    def connect(self, port):
        print("Connecting to power supply.")
        try:
            self.ser = serial.Serial(port=port, baudrate=1200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.SEVENBITS, xonxoff=False, rtscts=False, dsrdtr=False, timeout=1)
            success = True
        except serial.serialutil.SerialException:
            print("Error: Could not connect to power supply.")
            success = False
        return success
    
    def disconnect(self):
        if self.ser == False:
            print("Error: Not connected to power supply!")
        else:
            self.ser.close()
        return
    
    def writeVoltage(self, voltage, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nVOLT "+str(voltage).encode()+b"\n")
        return
    
    def writeCurrent(self, current, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nCURR "+str(current).encode()+b"\n")
        return
    
    def readVoltage(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nMEAS:VOLT?\n")
        voltage = self.read()
        return float(voltage.strip())
    
    def readCurrent(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nMEAS:CURR?\n")
        current = self.read()
        return float(current.strip())
    
    def readTargetVoltage(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nVOLT?\n")
        voltage = self.read()
        return float(voltage.strip())
    
    def readTargetCurrent(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nCURR?\n")
        current = self.read()
        return float(current.strip())
    
    def powerOn(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nOUTP ON\n")
        return
    
    def powerOff(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nOUTP OFF\n")
        return
    
    def readPower(self, channel):
        self.write(b"INST OUT"+str(channel).encode()+b"\nOUTP STAT?\n")
        state = self.read()
        return state
    
    def readDeviceName(self):
        # self.write(b"IDN?\n")
        # deviceName = self.read()
        deviceName = "HMP4040"
        return deviceName
    
    def read(self):
        '''
        This function will wait until the power supply sends some stuff to the port, and then it will wait until it doesn't send
        stuff anymore. Don't use it when you don't expect the power supply to send you anything !!
        '''
        if self.ser == False:
            print("Error: Not connected to power supply!")
            returnString = "0"
        else:
            returnString = self.ser.readline()
            returnString = returnString.decode()
        return returnString
    
    def write(self, stuff):
        '''
        Writes stuff into the serial port and waits for 50 milliseconds so that the next message doesn't get lost.
        Stuff must be bytes.
        '''
        if self.ser == False:
            print("Error: Not connected to power supply!")
        else:
            self.ser.write(stuff)
            #time.sleep(0.05)
        
        
        