#!/usr/bin/python

import cv
import sys, socket
import time


if len(sys.argv)<3:
    print "arguments missing..."
    print "Usage: CamClient.py SERVER PORT [DEBUG]"
    print "   SERVER = server IP or hostname"
    print "   PORT = server port number"
    print "   DEBUG = [True|False] (optional)"
    sys.exit()


HOST = sys.argv[1]
MPORT = int(sys.argv[2])
cv.NamedWindow("w2", cv.CV_WINDOW_AUTOSIZE)
camera_index = 0
count = 0;

DEBUG = False
if len(sys.argv)>3 and sys.argv[3] == 1:
    DEBUG = True


def log (string):
    if DEBUG:
        print string

class VideoClient():
    def start(self):
        self.connectionStatus = "connecting"
        self.filename = "recievedImage.jpg"
        self.port = 9092
        self.lastTime = time.time()
        self.fps = 0
        self.frameNum = 0
        self.timePassed = 0

        self.setup()
        self.setupTransfer()
        while 1:
            self.getMessage()
            if self.connectionStatus ==  "connecting":
                self.listen()
            self.getImage()
            self.displayImage()

        self.closeTransferConnection()
        self.close()




    def setup(self):
        log ("setting up message connection")
        self.msock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msock.connect((HOST, MPORT))

    def setupTransfer(self):
        log ("setting up transfer connection")
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.bind(('',0))
        self.port = self.ssock.getsockname()[1]
        log ( "listening on: "+ str(self.port))
        self.ssock.listen(5)

    def listen(self):
        self.connectionStatus = "connected"
        log ("listening for transfer")
        self.sconn, self.saddr = self.ssock.accept()

    def getMessage(self):
        log( "sending port")
        portSt = str(self.port)
        while len(str(portSt)) <5:
            portSt = "0"+portSt
        message = "transferPort="+portSt
        log( "messageSize: " + str(len(message)))
        self.msock.send(message)



    def getImage(self):
        log( "getting image")
        global camera_index
        global count

        msg = ''
        msgSize = 6
        while len(msg) < 6:
            chunk = self.sconn.recv(msgSize-len(msg))
            if chunk == '':
                raise RuntimeError('connectino lost')
            msg = msg + chunk
        log ("msg:'" + msg + "'")
        size = int(msg)
        log ("size of file:" + str(size))
        #chunksize = 1024

        f = open(self.filename,"wb")
        filedata = ''
        while len(filedata)<size:
            chunk = self.sconn.recv(size-len(filedata))
            if chunk == '':
                raise RuntimeError('connectino lost')
            filedata = filedata + chunk

        f.write(filedata)
        f.close()
        count = count + 1
        self.calculateFPS()

    def displayImage(self):
        log( "Showing image")
        global capture #declare as globals since we are assigning to them now
        global camera_index
        global count

        frame = cv.LoadImageM(self.filename)
        font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, 0, 1)
        cv.PutText(frame,"fps:"+str(round(self.fps,2)), (0,30),font,(255,255,255,0))
        cv.ShowImage("w2", frame)
        cv.WaitKey(10)

    def calculateFPS(self):
        oldTime = self.lastTime;
        self.lastTime = time.time()
        self.timePassed = self.timePassed+ self.lastTime - oldTime
        self.frameNum = self.frameNum + 1
        #print self.timePassed
        if self.timePassed > 1:
            self.fps = self.frameNum / self.timePassed
            self.timePassed = 0
            self.frameNum = 0



    def closeTransferConnection(self):
        log ("closing transfer connection")
        self.sconn.close()
        self.ssock.close()

    def close(self):
        log ("closing message connection")
        self.msock.close()



client = VideoClient()
client.start()


