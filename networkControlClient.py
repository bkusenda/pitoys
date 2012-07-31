#!/usr/bin/python
import serial
import os
import sys
import time
import socket

commandNameMap = {'9': "accelerate", '4': "turn left", '6':"turn right",'5': "stop",'3':"reverse"}
commandActionMap =  {"0 1 2":'9',"0 1 1":'3',"128 2 4":'4',"127 2 4":'6'}


class JoyListener():
    def start(self,control):
        pipe=open("/dev/input/js0","r")
        data = []
        while 1:
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
                        control.sendCommand(commandAction);
                    data = []


class NetworkListener():

        def start(self,control):
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
                    control.sendCommand(data)
                    client.send("command executed:" + data)


class NetworkControl(object):

    def __init__(self):
        self.host = '192.168.69.116'
        self.port = 50000
        self.size = 1024
        print "starting network control \n"

    def sendCommand(self,command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host,self.port))
        sock.send(str(command))
        data = sock.recv(self.size)
        print 'Received:', data
        sock.close()


class SerialControl(object):

    def __init__(self):
        self.ser = serial.Serial(
                port='/dev/ttyACM0',
                baudrate=9600,timeout=0
            #    parity=serial.PARITY_EVEN,
            #    bytesize=serial.EIGHTBITS
                )
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

control = NetworkControl()
joy = JoyListener()
joy.start(control)
