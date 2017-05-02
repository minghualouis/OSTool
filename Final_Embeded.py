#!/usr/bin/env python 

from socket import *
import sys
import getpass
try:
    import pwd
    import grp
except ImportError:
    import winpwd as pwd
    import win32net

import platform

def get_listening_ports():
    print("Below are the ports open in this computer: \n")
    Port = 0 #First port.
    while Port <= 65535: #Port 65535 is last port you can access.
        try:
            try:
                Socket = socket(AF_INET, SOCK_STREAM, 0) #Create a socket.
            except:
                print("Error: Can't open socket!\n")    
                break #If can't open socket, exit the loop.
            Socket.connect(("0.0.0.0", Port)) #Try connect the port. If port is not listening, throws ConnectionRefusedError. 
            Connected = True
        except ConnectionRefusedError:
            Connected = False       
        finally:
            if(Connected and Port != Socket.getsockname()[1]): #If connected,
                print("Port {} Is Open \n".format(Port)) #print port.
            Port = Port + 1 #Increase port.
            Socket.close() #Close socket.

def get_current_user():
    print("Current User is: {} \n".format(getpass.getuser()))

def get_user_group():
    if platform.system() == "Linux":
        for p in pwd.getpwall():
            print ("User: {}; Group: {}".format(p[0], grp.getgrgid(p[3])[0]))
    elif platform.system() == "Windows":
        for p in pwd.getpwall():
            for groups in win32net.NetUserGetLocalGroups(platform.uname()[1],p[0]):
                print ("User: {}; Group: {}".format(p[0], groups))
        
if __name__ == "__main__":
    if sys.argv[1] == "p":
        get_listening_ports()
    elif sys.argv[1] == "u":
        get_current_user()
    elif sys.argv[1] == "g":
        get_user_group()
    else:
        print("Error with the input, please check the command and arguments")
    
    
    