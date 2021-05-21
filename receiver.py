from sys import argv
import serial
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import struct
import os

#Default Variables
checkPreamble = False
checkPostamble = False

#Preamble listener
# def waitPreamble(ser):
#     i=0
#     #a = 0x00
#     while 1:
#         if ser.in_waiting>0:
#             try:
#                 a=ord(ser.read(1))
#                 print(a)
#             except:
#                 pass
#             if a == 0x55:  # //sorun yokmuş eski haline aldım. print edince 85 alıyo
#                 i=i+1
#             elif a== 0x0 and i>100:   
#                 checkPreamble = True
#                 print('\n preample True')
#                 break
#             else:
#                 checkPreamble = False

def waitPresign(ser):
    i = 0                
    while True:
        a = ord(ser.read(1))
        if a == 0x55:
            i = i+1
        elif a == 0x0 and i>100:
            return True
        else:
            mb.showerror("Preamble Error", "Bad Data: 0x%x"% ord(ser.read(1)))      

#Postamble
def isPostsign(postval):
    if len(postval)<101:
        return False
    i=0
    for a in postval:
        if a == 0x55:
            if i == 100:
                print('\n postsignal True')
                return True
            elif i>0:
                i=i+1
        elif a == 0x0:
            if i == 0:
                i=i+1          
            else:
                return False
        else:
            return False

#Postamble Value Updater
def updatePostval(postval, xy):
    msg=[]
    ex = (len(postval)+len(xy))-101 #extra length
    if ex > 0:
        for i in range(0, ex+1):
            msg.append(postval.pop(0))
    postval.extend(xy)
    return msg

def startReceive(ser):
    waitPresign(ser)
    files=[('Text Document','*.txt')]
    file = fd.asksaveasfile(mode='wb', filetypes=files, defaultextension=files) #Open txt. file asking the user for name and directory.
    fpath = file.name
    #waitPresign(ser)
    #if checkPreamble == False:
        #mb.showerror("Connection Error", "Preamble message not received")
    postval = []
    mb.showinfo("File", "Receiving the incoming File")
    while True:
        comingMsg = ser.read(1)
        xy=comingMsg
        msg=updatePostval(postval, xy)
        if isPostsign(postval):
            
            break
        msg = ''.join(list(map(chr, msg))) #yeri değiştirildi
        file.write(msg.encode('utf8')) #veri tipini kabul etmediğinden byte-str dönüşümü yapıldı

    file.close() #Close the file.
    ser.flush() #Buffer clear. 

    mb.showinfo("File", "File saved.")
    os.system(fpath)
    return startReceive(ser)
    

def listenKey(ser):
    waitPresign(ser)
    key = ser.readline()
    #struct.unpack('11B', key)
    ints = list(key)
    #ints = map(ord,key)
    return ints[0]
 
def listenKeyGen(ser):
    #waitPresign(ser)
    rkey = ser.readline()
    key = rkey.decode('utf-8')
    return key