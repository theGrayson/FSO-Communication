from sys import argv
import tkinter as tk #module to open windows file selector
from tkinter import filedialog
import serial
import struct


#Preamble
def sendPresign(ser):
    for i in range (0, 110):#2000 cok fazla
        ser.write([0x55])
    ser.write([0x0])

#Postamble        
def sendPostsign(ser):
    ser.write([0x0])
    for i in range (0, 110):#2000 cok fazla
        ser.write([0x55])
    
#Sending File
def sendFile(ser, path):
    f = open(path, "rb")
    while True:
        c=f.read(1024)
        if len(c) > 0:
            ser.write(c)
            print(c)
        else:
            break

def startTransmit(ser, path):
    sendPresign(ser)
    sendFile(ser,path)
    sendPostsign(ser)

#Authentication Key-Exchange

def sendKey(ser, key):
    sendPresign(ser)
    # ser.write(key)
    string = struct.pack('!B', key)
    ser.write(string)
   #sendPostsign(ser)


def sendKeyGen(ser,key):
    #sendPresign(ser)
    msg = key.encode('utf-8')
    ser.write(msg)

   
