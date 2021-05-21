from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import serial
import sender
import receiver
import auth
import threading
import time

#global variables
port = "COM5"
baud = 1200
isAuth = False
isPortOpen = False

#root widget
root = Tk(className=' FSO Transfer App')
root.geometry("400x400") 
root['background']='#3C3C3C'

#Define settings window
def openSettings():
    global settingWindow
    try:
        if settingWindow.state()=="normal": settingWindow.focus()
    except: 
          
        settingWindow = Toplevel(root)
        settingWindow.geometry("400x300")
        settingWindow['background']='#3C3C3C'
        
        portLabel = Label(settingWindow, text="Current used Port for the Hardware is " + port, font=14, bg='#3C3C3C', fg = 'white') 
        portLabel.place(relx=0.5, rely=0.2, anchor=CENTER)
        portEntry = Entry(settingWindow)
        portEntry.place(relx=0.5, rely=0.3, anchor=CENTER)
        portEntry.delete(0,END)
        portEntry.insert(0, port)

        baudLabel = Label(settingWindow, text="Current active Baud Rate is " + str(baud) + " bps", font=14, bg='#3C3C3C', fg = 'white') 
        baudLabel.place(relx=0.5, rely=0.4, anchor=CENTER)
        baudEntry = Entry(settingWindow)
        baudEntry.place(relx=0.5, rely=0.5, anchor=CENTER)
        baudEntry.delete(0,END)
        baudEntry.insert(0, baud)

        def save():
            global port
            global baud
            port = portEntry.get()
            baud = baudEntry.get()
            mb.showinfo("Settings", "Settings Saved")
            settingWindow.focus()
                       

            if isPortOpen == True:
                ser.close()
                isPortOpen == False          
                   
                        
            portLabel.configure(text="Current used Port for the Hardware is " + port)
            baudLabel.configure(text="Current active Baud Rate is " + str(baud) + " bps")


        saveButton = Button(settingWindow, text="Save Changes", font=14, bg='#818080', fg = 'white', command = save)
        saveButton.place(relx=0.5, rely=0.7, anchor=CENTER)

#Define transceiver window
def openTransceiver():
    global transceiverWindow

    try:
        print(ser.name)
    except:    
        mb.showerror("COM Error", "Communication port Error")  

    try:
        if transceiverWindow.state() == "normal": transceiverWindow.focus()
    except:    
        transceiverWindow = Tk(className = ' FSO Transceiver')
        transceiverWindow.geometry("400x400")
        transceiverWindow['background'] = '#3C3C3C'

        transceiverLabel = Label(transceiverWindow, text="FSO Transceiver", font=24, bg='#3C3C3C', fg = 'white')
        transceiverLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

        authLabel = Label(transceiverWindow, text = "Authentication is not Complete, Please Authenticate.", font=8, bg='#3C3C3C', fg = 'white')
        authLabel.place(relx=0.5, rely=0.2, anchor=CENTER)
        
        settingLabel = Label(transceiverWindow, text="Port: " + port + " Baud Rate: " + str(baud) + " bps", font=8, bg='#3C3C3C', fg = 'white')
        settingLabel.place(relx=0.5, rely=0.3, anchor=CENTER)

        pathLabel = Label(transceiverWindow, text="File selected: " + "NONE", font=24, bg='#3C3C3C', fg = 'white')
        pathLabel.place(relx=0.5, rely=0.4, anchor=CENTER)

        statusLabel = Label(transceiverWindow, text='Select your File', font=24, bg='#3C3C3C', fg = 'white')
        statusLabel.place(relx=0.5, rely=0.5, anchor=CENTER) 


        def selectFile():
            try:
                #path global yapıldı erişilemiyordu.  
                global path
                path = fd.askopenfilename()
                pathLabel.configure( text="File selected: " + path)
                statusLabel.configure( text="Press Send File")
                  
            except:
                mb.showerror("File Error","Can not select the file!")
                        
            try:
                f = open(path, "rb")
                c=f.read(2048)
                sendButton.configure(state=NORMAL)  
                #print(c)
            except:
                mb.showerror("File Error","Can not open the file!")
                

        def sendFile():
            sender.startTransmit(ser, path)

        def listenFile():
            time.sleep(2)
            receiver.startReceive(ser)
        
        fileButton = Button(transceiverWindow, text="Select File", font=14, bg='#818080', fg = 'white', command = selectFile, state=DISABLED)
        fileButton.place(relx=0.5, rely=0.6, anchor=CENTER) 

        sendButton = Button(transceiverWindow, text="Send File", font=14, bg='#818080', fg = 'white', command = sendFile, state=DISABLED)
        sendButton.place(relx=0.5, rely=0.7, anchor=CENTER)   

        #listenButton = Button(transceiverWindow, text="Listen File", font=14, bg='#818080', fg = 'white', command = threading.Thread(target=listenFile).start(), state=DISABLED)
        #listenButton.place(relx=0.5, rely=0.8, anchor=CENTER)        

        if isAuth == True:
            #listenButton.configure(state = NORMAL)
            fileButton.configure(state = NORMAL)
            listen = threading.Thread(target=listenFile, daemon=True)
            listen.start()
            authLabel.configure(text = "Authentication Complete")
                
#Define Authentication Window
def openAuth():
    global ser
    
    if isPortOpen == False:
        try: 
            ser = serial.Serial(port = port, baudrate= baud, bytesize=8, timeout=3, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_ODD)
            isPortOpen == True
        except:
            ser.close()
            ser = serial.Serial(port = port, baudrate= baud, bytesize=8, timeout=3, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_ODD) 
    
    partialKey = auth.generateKey()
    
    try:
        mb.showinfo("Authentication", "Please Wait Until Authentication is Completed. \n This Process can take some time.")
        time.sleep(5)
        sender.sendKey(ser, partialKey)
        print("My Key: " , partialKey)
        try:
            exchangeKey = receiver.listenKey(ser)
            print("Other Key: " , exchangeKey)
            time.sleep(5)
            try:
                keygen1 = auth.computeKey(exchangeKey)
                print("My Keygen: " , keygen1)
                sender.sendKeyGen(ser, keygen1)
                try:
                    keygen2=receiver.listenKeyGen(ser)
                    print("Other Keygen: " , keygen2)
                    if keygen1 == keygen2:
                        global isAuth
                        isAuth = True
                        ser.timeout=None
                        ser.flush()
                        mb.showinfo("Authentication", "Authentication is complete.") 
                    else: mb.showerror("Authentication", "Authentication Failed")      
                except: 
                    mb.showerror("Authentication", "Authentication Failed")            
            except: 
                mb.showerror("Authentication", "Problem During Keygen transmission")
        except:
            mb.showerror("Authentication","Error receiving the partial key")
    except:
        mb.showerror("Authentication", "Error sending the partial key")
  
#Creating a Text Label Widget
projectLabel = Label(root, text="Free Space Optical Transfer App", font=24, bg='#3C3C3C', fg = 'white') 
projectLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

#Creating Auth Button
authButton = Button(root, text="Authentication", font=24, bg='#818080', fg = 'white', command = openAuth)
authButton.place(relx=0.5, rely=0.3, anchor=CENTER)

#Creating Transceiver Button
transceiverButton = Button(root, text="Transceiver", font=24, bg='#818080', fg = 'white', command = openTransceiver)
transceiverButton.place(relx=0.5, rely=0.4, anchor=CENTER)

#Creating Settings Button
settingsButton = Button(root, text="Settings", font=24, bg='#818080', fg = 'white', command = openSettings)
settingsButton.place(relx=0.5, rely=0.5, anchor=CENTER)

def openInst():
    mb.showinfo("Instructions", "1-From Settings choose the COM port in usage and the Baud Rate.\n 2-Authenticate yourself. \n 3-Open the Transceiver.")

#Creating Instructions Button
instButton = Button(root, text="Instructions", font=24, bg='#818080', fg = 'white', command = openInst)
instButton.place(relx=0.5, rely=0.6, anchor=CENTER)

root.mainloop()
