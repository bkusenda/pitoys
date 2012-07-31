#!/usr/bin/python
# USAGE: python FileReciever.py

import socket, time, string, sys, urlparse, cv
from threading import *

#------------------------------------------------------------------------

if len(sys.argv)<2:
    print "Arguments missing..."
    print "Usage: CamServer.py PORT [DEBUG]"
    print "   PORT = port number"
    print "   DEBUG = [True|False] (optional)"
    sys.exit()


camera_index = 0
capture = cv.CaptureFromCAM(camera_index)
count = 0

SPORT = int(sys.argv[1])

DEBUG = False
if len(sys.argv)>2 and sys.argv[2] == 1:
    DEBUG = True
   

SHOWERROR = False

def log(string):
    if DEBUG:
        print string

def logError(string):
    global SHOWERROR
    if SHOWERROR == False:
        print string
        SHOWERROR = True

class StreamHandler ( Thread ):



    def __init__( this ):
        Thread.__init__( this )
        this.props = dict()
        this.props["serverPort"]=SPORT

    def run(this):
        this.connectionStatus = "connecting"
        this.process()


    def process( this ):
        this.setupServer();
        this.listenForConnections()
        while 1:
            this.getMessageFromClient()
        this.closeTransferConnection()
        this.close()

    def setupServer( this ):
        log ("setting up server")
        this.msock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        this.msock.bind(('', int(this.props["serverPort"])))
        #this.msock.bind(('', SPORT))
        this.msock.listen(5)
        log('Listening on port '+ str(this.props["serverPort"]))

    def listenForConnections( this ):
        log ("listening for connections")
        this.mconn, this.maddr = this.msock.accept()
        log('Got connection from ' + str(this.maddr))

    def getMessageFromClient( this ):
        log ("status="+this.connectionStatus)
        size=18
        msg = ''
        while len(msg) < size:
            chunk = this.mconn.recv(size - len(msg))
            if chunk == '':
                raise RuntimeError("socken connectin broken")
            msg = msg + chunk
        command = "nextFrame"
        if msg != '':
            log( "Recieved:"+msg)
            value = str(msg).split('=')
            if len(value) == 2:
                log( "("+value[0] + "," + value[1] + ")")
                if value[0]=="command":
                    command = value[0]
                else:
                    this.props[str(value[0])] = value[1]
            this.processMessage(command)
        else:
            logError( "Error: no data recieved")

    def processMessage(this,command):

        if command == "nextFrame":
           this.sendFile();

    def setupTransferConnection(this):
        log ("setting up transfer connection on port:" + str(this.props["transferPort"]))
        #cv.WaitKey(300)
        this.csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        this.csock.connect((this.maddr[0], int(this.props["transferPort"])))
        this.connectionStatus = "connected"

    def closeTransferConnection(this):
        log ("closing transfer connection")
        this.csock.close()

    def sendFile(this):
        log ("Sending file");
        global capture #declare as globals since we are assigning to them now
        global camera_index
        global count
        filename = "cv.jpg"
        frame = cv.QueryFrame(capture)
        cv.SaveImage(filename,frame)
        f = open(filename,"rb")
        data = f.read()
        f.close()
        if this.connectionStatus == "connecting":
            this.setupTransferConnection()

        length_st = str(len(data))
        log( "strsize="+str(len(length_st)))
        log( "chunk size:"+ length_st)
        while len(str(length_st)) <6:
            length_st = "0"+length_st

        this.csock.send(length_st)
        this.csock.send(data)
        log ("fileSent")
        count = count + 1



    def close( this ):
        this.mconn.close()
        this.msock.close()

s = StreamHandler()
s.start()
print "Server Started"
