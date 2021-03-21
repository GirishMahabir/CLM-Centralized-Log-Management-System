#!/usr/bin/env python3.7
"""
Client-Side Script.
Sends logs to the server. 
"""
import socket, os, time, sys, threading, concurrent.futures

# Global Constant Values.
HEADER = 64 # size of incoming messages. Size in byte.
PORT = 8975 # Using PORT 8975
SERVER = "10.10.10.61" # Server IP.
ADDR = (SERVER,PORT) # This should be a tuple.
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
PING_MSG = "!PING"
# Add files you want to be monitorted here seperated by a "," .
FilesToMonitor = ["/var/log/syslog"]
# Insert ports that are allowed to be open on the system.
# port in the ALLOW list will not be reported.
ALLOW = [22,80,443,3306] # ssh, http, https, mysql 
# You can put scanning to False to disable scanning.
SCANNING = True
LOCALIP = "10.10.10.35" # Local IP Address.

# Client Socket.
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
client.connect(ADDR)

def send(msg):
    """
    This function will take an argument as a string and send it to the server.
    Get the length of the message. Send the length to the server so as to make
    provision for the coming message.
    
    Args:
        msg, msg to send to server.
    
    returns:
        None
    """
     # To send we need to encode the msg into a byte.
    message = msg.encode(FORMAT)
    msg_length = len(message) # Get the length of the message.
    # send the incomming msg length to the server to make provison for the 
    # comming message length.
    send_length = str(msg_length).encode(FORMAT)
    # Our initial HEADER is 64, we will add ' ' to adjust for that.
    send_length += b' ' * (HEADER - len(send_length))
    # This will add blank space to make the msg length 64 byte.
    client.send(send_length)
    client.send(message)
    """
    Handling msg receiving from server!
    print(client.recv(1024).decode(FORMAT))
    """

def logStreamMonitor(toMonitor):
    '''
    Constantly check for new line in log file and pass string to the send
    module.

    Args:
        toMonitor = Files to be monitored.
    returns:
        None
    '''
    logFile = open(toMonitor)
    logFile.seek(0,os.SEEK_END)# Move file pointer 0 bytes from end of file.
    while True:
        line = logFile.read()
        if line == '':
            time.sleep(0.1) # wait briefly and retry.
            continue
        send(line)

def logThread():
    '''
    For each log file a thread will handle the monitoring.
    '''
    for item in FilesToMonitor:
        file_thread = threading.Thread(target=logStreamMonitor,args=(item,))
        file_thread.start()

def scan(port,LOCALIP):
    '''
    Function to scan for one open port.
    
    Args:
        port, port to scan.
        LOCALIP, IP to scan for that port.
    Returns:
        None
    
    It sends a string to the send function to send to the server.
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((LOCALIP,port))
        # 111 => Connection refused.
        # 106 => Transport endpoint is already connected.
        # 0 => Success
        if result == 0 and port not in ALLOW:
            send(f"Port Open Alert: {str(port)}")
    except socket.gaierror:
        print("Host could not be resolved")
    except socket.error:
        print("Couldn't connect to server")
    finally:
        sock.close()

def ScanBreak():
    """
    Send each port to scan one by one.
    """
    while SCANNING:
        for port in range(1,65536):
            scanThread = threading.Thread(target=scan, args= (port,LOCALIP,))
            scanThread.start()

def ping():
    """
    Ping function to ping the server at a given time interval.
    This is important to let the server know that the client is still alive and
    also to clean disconnect any dead client.
    """
    while True:
        send(PING_MSG)
        time.sleep(250)

def ThreadPing():
    """
    Function that starts a thread to ping the server.
    """
    threadping = threading.Thread(target=ping)
    threadping.start()

def ThreadScan():
    """
    Function that starts thread to deal with scanning of the server.
    """
    ScanBreakThread = threading.Thread(target=ScanBreak)
    ScanBreakThread.start()
   #print("Started Scan!")

def main():
    #print(f"[STARTING]...Sending Logs to {SERVER}.")
    #print("Starting Ping.")
    ThreadPing()
    #print("Starting Scan.")
    ThreadScan()
   # print("Started Logging.")
    logThread()
    #print("Exitting main Thread")

if __name__=="__main__":
    try:
        pid = os.fork()
        if pid > 0:
            # Exitting parent process
            sys.exit(0)
    except OSError:
        send(DISCONNECT_MSG)
        sys.exit(1)
    # Configuring the child processes environment.
    os.setsid()
    main()