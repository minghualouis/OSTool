from socket import *
import getpass
import pwd, grp

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
    for p in pwd.getpwall():
        print ("User: {}; Group: {}".format(p[0], grp.getgrgid(p[3])[0]))
        
if __name__ == "__main__":
    get_current_user()
    get_listening_ports()
    get_user_group()
    
    
    
    
    