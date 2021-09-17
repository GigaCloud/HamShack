import serial
import time
import os
import paramiko

f = open('config.txt', 'r')


HRD_port = f.readline().split()[0]
main_port = f.readline().split()[0]
host =  f.readline().split()[0]
port = int(f.readline().split()[0])
username = f.readline().split()[0]
password = f.readline().split()[0]

print('\n\n')
print("Citit configuratia:")
print("HRD: " + HRD_port + " Program: " + main_port)
print("Server: " + host + ":" + str(port))
print("User: " + username)

mute_cmd   = "sudo -u pulse pactl set-source-mute @DEFAULT_SOURCE@ true"
unmute_cmd = "sudo -u pulse pactl set-source-mute @DEFAULT_SOURCE@ false"
ser = serial.Serial(main_port)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

print("Waiting - set DTR from wsjt or jtdx")

serial.Serial(HRD_port).close()

aux = True

#pactl set-sink-mute @DEFAULT_SINK@ true

while True:
    #if not ssh.is_active():
    #    print("NU E CONECTAT SSH-UL - vezi ce are si reporneste!")
        
    if int(ser.dsr) == 1 and aux:
        print("DTR active from " + main_port + " PTT ON\n")
        aux = False
        ssh.exec_command(mute_cmd)
        
    if int(ser.dsr) == 0 and not aux:
        aux = True
        print("PTT off\n")
        ssh.exec_command(unmute_cmd)

