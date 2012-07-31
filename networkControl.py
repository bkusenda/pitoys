#!/usr/bin/python
import serial
import os
import sys
import time
import socket

commandNameMap = {'9': "accelerate", '4': "turn left", '6':"turn right",'5': "stop",'3':"reverse"}
commandActionMap =  {"0 1 2":'9',"0 1 1":'3',"128 2 4":'4',"127 2 4":'6'}


class JoyRead():
    def start(self,mcontrol):
        pipe=open("/dev/input/js0","r")
        data = []
        while 1:
            mcontrol.printFromSerial()
            for char in pipe.read(1):
                data += [ord(char)]
                if len(data) == 8:
                    datast = "";
                    buttonst ="";
                    bytecount = 0
                    for c in data:
                        if bytecount >=4 :
                            datast += " "+repr(c)
                        if bytecount >4 :
                            buttonst += " "+repr(c)

                        bytecount += 1;
                    print("  "+datast + "\n")
                    commandAction = commandActionMap.get(buttonst.strip(),'-1')
                    if(commandAction != '-1'):
                        commandName = commandNameMap[commandAction]
                        print("command="+commandName)
                        mcontrol.sendCommand(commandAction);
                    data = []

class NetworkRead():

        def start(self,mcontrol):
            host= ''
            port = 50000
            backlog = 5
            size = 1024
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.bind((host,port))
            s.listen(backlog)

            while 1:
                client, address = s.accept()
                data = client.recv(size)
                if data:
                    print "Recieved Command:"+data
                    mcontrol.sendCommand(data)
                    client.send("command executed:" + data)





class MControl(object):
#    ser = serial.Serial('/dev/ttyACM0')
    ser = serial.Serial(
                port='/dev/ttyACM0',
                baudrate=9600,timeout=0
            #    parity=serial.PARITY_EVEN,
            #    stopbits=serial.STOPBITS_TWO,
            #    bytesize=serial.EIGHTBITS
                )
    def __init__(self):
         self.printFromSerial()

    def sendCommand(self,command):
        self.ser.write(command)
        self.printFromSerial()

    def printFromSerial(self):
        print "reading..."
        self.readSerial()

    def readSerial(self):
        output = self.ser.readall();
        print (output)

        #while self.ser.inWaiting() > 0:
        #    out += self.ser.read(1)
        #    if out != '':
        #        print ">>" + out

    def shutdown(self):
        self.sendCommand('0')
        self.stop()
        self.ser.close()

mcontrol = MControl()
#joy = JoyRead()
#joy.start(mcontrol)
network = NetworkRead()
network.start(mcontrol)
print "Quiting"

