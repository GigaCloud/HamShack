import time
import os
import paramiko

import tkinter as tk

f = open('config.txt', 'r')


host =  f.readline().split()[0]
port = int(f.readline().split()[0])
username = f.readline().split()[0]
password = f.readline().split()[0]

print('\n\n')
print("Citit configuratia:")
print("Server: " + host + ":" + str(port))
print("User: " + username)

mute_cmd   = "sudo -u pulse pactl set-source-mute @DEFAULT_SOURCE@ true"
unmute_cmd = "sudo -u pulse pactl set-source-mute @DEFAULT_SOURCE@ false"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

window = tk.Tk()

window.title("Programel PTT")

aux = 1 #adica mut

def mute():
    ssh.exec_command(mute_cmd)

def unmute():
    ssh.exec_command(unmute_cmd)


buttonPTT = tk.Button(
    text="PTT",
    width=25,
    height=5,
    bg="#eda600",
    activebackground="#db9a00"
)

def toggle(): #presupunem ca e pe mut
    global aux
    if (aux == 1):
        print("Am dat unmute")
        unmute()
        aux = 0
        buttonPTT.configure(bg = "#96ed00")
        buttonPTT.configure(activebackground="#84d100")
        buttonPTT.configure(text = "PTT - poti vorbi!")
    else:
        print("Am dat mute")
        buttonPTT.configure(bg = "#eda600")
        buttonPTT.configure(activebackground="#db9a00")
        buttonPTT.configure(text = "PTT - esti pe mut!")
        mute()
        aux = 1

buttonPTT.configure(command = toggle)

buttonPTT.pack()

mute() #ne asiguram ca pornim programul cu mut

window.mainloop()
