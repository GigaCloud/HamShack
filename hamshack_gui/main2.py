#WINDOWS ONLY ca fac o carpeala ca sa pasez com-urile ca int COM42 -> 42(int)
#plus ca e ceva manevra la multiprocessing de merge doar pe windows in config actuala
import pathlib
import tkinter as tk
import tkinter.ttk as ttk
import pygubu
from pygubu.builder import tkstdwidgets

PROJECT_UI = "lol.ui"

import time
import os
import paramiko
import sys
import tkinter as tk

from datetime import datetime

import json

import serial
import multiprocessing

import subprocess
from subprocess import DEVNULL

global log 
log = open('log.txt', 'w')

global runWSJT
global comWSJT
global comPTT
runWSJT = multiprocessing.Value("i", 1)
comWSJT = multiprocessing.Value("i", 0)
comPTT  = multiprocessing.Value("i", 0)

def printLog(text):
    now = datetime.now()
    global log
    print(str(now) + "\t" + text, file=log, flush=True)
    print(str(now) + "\t" + text, flush=True)

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(str(port))
        except (OSError, serial.SerialException):
            pass
    return result


def PTT_WSJTRoutine(configJSON, runWSJT, comWSJT, comPTT):
    try:
    
        host =  configJSON["ssh"]["server"]
        port =  int(configJSON["ssh"]["port"])
        username = configJSON["ssh"]["user"]
        password = configJSON["ssh"]["pass"]
        mute_cmd   = configJSON["PTT"]["mute_cmd"]
        unmute_cmd = configJSON["PTT"]["unmute_cmd"]
        
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
            
        WSJT_port = configJSON["serialPTT_WSJT"]["comWSJT"]
        main_port = configJSON["serialPTT_WSJT"]["comPTT"]
        ser = serial.Serial(main_port)
        
        aux = True
        while True:
            if runWSJT.value == 1:
                if ser.isOpen() == False: #reconfigureaza serialul
                    printLog("WSJT_PTT - Reconfigurat serialul")
                    WSJT_port = str("COM" + str(comWSJT.value))
                    main_port = str("COM" + str(comPTT.value))
                    ser = serial.Serial(main_port)
                    serial.Serial(WSJT_port).close()
                
                if int(ser.dsr) == 1 and aux:
                    printLog("DTR active from " + main_port + " PTT ON\n")
                    aux = False
                    ssh.exec_command(mute_cmd)
                    
                if int(ser.dsr) == 0 and not aux:                    
                    aux = True
                    printLog("PTT off\n")
                    ssh.exec_command(unmute_cmd)
                   
            elif runWSJT.value == 0:
                try:
                    ser.close()
                except:
                    pass
                
    except Exception as e:
        printLog("WSJT_PTT: " + str(e))
        
        


global procesSerialNetwork
global procesRecAudio
global procesTraAudio

if __name__ == "__main__":
    multiprocessing.freeze_support() #sa-l pot face .exe dupa
    

  #  multiprocessing.set_start_method('spawn')

    configFile = open('config.json', 'r')

    configJSON = json.loads(configFile.read())

    configFile.close()

    host =  configJSON["ssh"]["server"]
    port =  int(configJSON["ssh"]["port"])
    username = configJSON["ssh"]["user"]
    password = configJSON["ssh"]["pass"]
    
    comWSJT.value = int(str(configJSON["serialPTT_WSJT"]["comWSJT"]).replace("COM", ''))
    comPTT.value = int(str(configJSON["serialPTT_WSJT"]["comPTT"]).replace("COM", ''))

    printLog("Citit configuratia:")
    printLog("Server: " + host + ":" + str(port))
    printLog("User: " + username)

    #mute_cmd   = "sudo -u pulse pactl set-source-mute @DEFAULT_SOURCE@ true"
    #unmute_cmd = "sudo -u pulse pactl set-source-mute @DEFAULT_SOURCE@ false"
    #nu uita sa bagi astea in config.json la final

    mute_cmd   = configJSON["PTT"]["mute_cmd"]
    unmute_cmd = configJSON["PTT"]["unmute_cmd"]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)


    procesSerialNetwork = subprocess.Popen(["com2tcp.exe", "--ignore-dsr", "--baud", configJSON['serialControlStatie']['baud'], '\\\\.\\' +  configJSON['serialControlStatie']['comPereche'],  configJSON['serialControlStatie']['ipIGEL'], configJSON['serialControlStatie']['port'] ])
    
    #print(str(configJSON["audio"]["traAudio"]).split(' '))
    procesTraAudio = subprocess.Popen(configJSON["audio"]["traAudio"].split(' '), stdout=DEVNULL)
    procesRecAudio = subprocess.Popen(configJSON["audio"]["recAudio"].split(' '), stdout=DEVNULL)

    def mutePTT():
        ssh.exec_command(unmute_cmd) #sunt invers ca trebuie sa dai inputu ala\ 
                                     #pe mut ca sa vorbesti (dubios, stiu)
    def unmutePTT():
        ssh.exec_command(mute_cmd)
      
    tk.builder = builder = pygubu.Builder()
    builder.add_from_file(PROJECT_UI)
    tk.mainwindow = builder.get_object('toplevel2')

    tk.__tkvar = None
    builder.import_variables(tk, ['__tkvar'])

    builder.connect_callbacks(tk)

    tk.mainwindow.title("Hamshack GUI")
    tk.mainwindow.geometry("400x650")

    global auxPTT
    auxPTT = 1 #adica mut
    mutePTT() #pornim programul cu PTT pe mut

    butonPTT = builder.get_object("butonPTT")
    butonPTT.configure(justify = "center")
    butonPTT.configure(width = "19")
    butonPTT.configure(height = "2")
    butonPTT.configure(bg = "#fa924c")
    butonPTT.configure(activebackground="#fa8638")
    butonPTT.configure(text = "PTT - esti pe mut!")


    def toggleaudioPTT(): #presupunem ca e pe mut
        global auxPTT
        if (auxPTT == 1):
            printLog("Am dat unmute PTT manual")
            unmutePTT()
            auxPTT = 0
            butonPTT.configure(bg = "#6baa75")
            butonPTT.configure(activebackground="#64a66f")
            butonPTT.configure(text = "PTT - poti vorbi!")
        else:
            printLog("Am dat mute PTT manual")
            butonPTT.configure(bg = "#fa924c")
            butonPTT.configure(activebackground="#fa8638")
            butonPTT.configure(text = "PTT - esti pe mut!")
            mutePTT()
            auxPTT = 1

    butonPTT.configure(command = toggleaudioPTT)

    procWSJT = multiprocessing.Process(target=PTT_WSJTRoutine, args=(configJSON, runWSJT, comWSJT, comPTT))

    def startWSJT():
        procWSJT.start()

    def stopWSJT():
        procWSJT.terminate()


    startWSJT()
    global auxWSJT
    auxWSJT = 1 #pornit initial

    butonWSJT = builder.get_object("butonWSJT")
    butonWSJT.configure(bg = "#6baa75")
    butonWSJT.configure(activebackground="#64a66f")
    butonWSJT.configure(text = "WSJT PTT On")
    butonWSJT.configure(justify = "center")
    butonWSJT.configure(width = "19")
    butonWSJT.configure(height = "2")

    def toggleWSJT(): #presupunem ca e pe mut
        global auxWSJT
        global runWSJT
        if (auxWSJT == 1):
            printLog("Opresc modul WSJT PTT")
            runWSJT.value = not runWSJT.value
            auxWSJT = 0
            butonWSJT.configure(bg = "#bf1a2f")
            butonWSJT.configure(activebackground="#b4182d")
            butonWSJT.configure(text = "WSJT PTT Off")
        else:
            printLog("Pornesc modul WSJT PTT")
            butonWSJT.configure(bg = "#6baa75")
            butonWSJT.configure(activebackground="#64a66f")
            butonWSJT.configure(text = "WSJT PTT On")
            runWSJT.value = not runWSJT.value
            auxWSJT = 1

    butonWSJT.configure(command = toggleWSJT)
    
    
    def schimbatWSJT(var):
        global comWSJT 
        comWSJT.value = int(str(var).replace("COM", ''))
       #print( int(str(var).replace("COM", '')))
       
    def schimbatPTT(var):
        global comPTT
        comPTT.value = int(str(var).replace("COM", ''))
        #print( int(str(var).replace("COM", '')))
    
    
    contextPTT = builder.get_object("butoanePTTFrame")
        
    varSerWSJT = tk.StringVar()
    varSerWSJT.set(configJSON["serialPTT_WSJT"]["comWSJT"])
    seriale = serial_ports()
    listaWSJT = tk.OptionMenu(contextPTT, varSerWSJT, *seriale, command=schimbatWSJT)
    listaWSJT.grid(row=2, column=2)
    printLog(str(serial_ports()))
    tk.Label(contextPTT, text="COM WSJT: ").grid(row=2, column=0)
    

    varSerPTT = tk.StringVar()
    varSerPTT.set(configJSON["serialPTT_WSJT"]["comPTT"])
    seriale = serial_ports()
    listaPTT = tk.OptionMenu(contextPTT, varSerPTT, *seriale, command=schimbatPTT)
    listaPTT.grid(row=3, column=2)
    printLog(str(serial_ports()))
    tk.Label(contextPTT, text="COM PTT: ").grid(row=3, column=0)
   
   
    serPereche = configJSON["serialControlStatie"]["comPereche"]
   
    def schimbatHRD(var):
        global serPereche
        serPereche = var
   
    contextSerial = builder.get_object("serialFrame")
    
    varSerHRD = tk.StringVar()
    varSerHRD.set(configJSON["serialControlStatie"]["comPereche"])
    seriale = serial_ports()
    listaHRD = tk.OptionMenu(contextSerial, varSerHRD, *seriale, command=schimbatHRD)
    listaHRD.grid(row=0, column=2)
    printLog(str(serial_ports()))
    tk.Label(contextSerial, text="COM Pereche HRD: ").grid(row=0, column=0)
    
    
    def restartSerial():
        global procesSerialNetwork 
        global serPereche
        procesSerialNetwork.terminate()
        time.sleep(0.5)
        procesSerialNetwork = subprocess.Popen(["com2tcp.exe", "--ignore-dsr", "--baud", configJSON['serialControlStatie']['baud'], '\\\\.\\' +  serPereche,  configJSON['serialControlStatie']['ipIGEL'], configJSON['serialControlStatie']['port'] ])
    
    butonSerial = builder.get_object("applySerial")
    butonSerial.configure(command = restartSerial)
    
    butonPrimeste= builder.get_object("butonPrimesteAudio")
    butonPrimeste.configure(bg = "#6baa75")
    butonPrimeste.configure(activebackground="#64a66f")
    butonPrimeste.configure(text = "Primeste Audio On")
    butonPrimeste.configure(justify = "center")
    butonPrimeste.configure(width = "19")
    butonPrimeste.configure(height = "2")
    
    butonTrimite = builder.get_object("butonTrimiteAudio")
    butonTrimite.configure(bg = "#6baa75")
    butonTrimite.configure(activebackground="#64a66f")
    butonTrimite.configure(text = "Trimite Audio On")
    butonTrimite.configure(justify = "center")
    butonTrimite.configure(width = "19")
    butonTrimite.configure(height = "2")
    
    global auxPrimeste
    auxPrimeste = 1
    
    global auxTrimite
    auxTrimite = 1
    
    def togglePrimeste():
        global auxPrimeste 
        global procesRecAudio
        if (auxPrimeste == 1):
            printLog("Opresc primeste audio")
            procesRecAudio.terminate()
            auxPrimeste = 0
            butonPrimeste.configure(bg = "#bf1a2f")
            butonPrimeste.configure(activebackground="#b4182d")
            butonPrimeste.configure(text = "Primeste Audio Off")
        else:
            printLog("Pornesc primeste audo")
            butonPrimeste.configure(bg = "#6baa75")
            butonPrimeste.configure(activebackground="#64a66f")
            butonPrimeste.configure(text = "Primeste Audio On")
            procesRecAudio = subprocess.Popen(configJSON["audio"]["recAudio"].split(' '), stdout=DEVNULL)
            auxPrimeste = 1
    
    butonPrimeste.configure(command=togglePrimeste)
    
    def toggleTrimite():
        global auxTrimite 
        global procesTraAudio
        if (auxTrimite == 1):
            printLog("Opresc Trimite audio")
            procesTraAudio.terminate()
            auxTrimite = 0
            butonTrimite.configure(bg = "#bf1a2f")
            butonTrimite.configure(activebackground="#b4182d")
            butonTrimite.configure(text = "Trimite Audio Off")
        else:
            printLog("Pornesc Trimite audo")
            butonTrimite.configure(bg = "#6baa75")
            butonTrimite.configure(activebackground="#64a66f")
            butonTrimite.configure(text = "Trimite Audio On")
            procesTraAudio = subprocess.Popen(configJSON["audio"]["traAudio"].split(' '), stdout=DEVNULL)
            auxTrimite = 1
    
    butonTrimite.configure(command=toggleTrimite)
    
    tk.mainwindow.mainloop()
