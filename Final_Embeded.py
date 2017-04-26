import socket
import getpass
import pwd, grp

def get_listening_ports():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    for i in range(1,65535):
        result = s.connect_ex(('0.0.0.0', i)) 
        if result == 0:
            print('Port %d socket is open' %i)

    s.close()

def get_current_user():
    print(getpass.getuser())

def get_user_group():
    for p in pwd.getpwall():
        print (p[0], grp.getgrgid(p[3])[0])
        
if __name__ == "__main__":
    get_current_user()
    get_listening_ports()
    get_user_group()