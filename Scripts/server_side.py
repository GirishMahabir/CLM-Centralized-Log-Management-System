#!/usr/bin/env python3.7

import socket, sys, os, time
import threading # To handle multiple clients.

# Global Constant Values.
HEADER = 64 # size of length of incoming messages. Size in byte.
PORT = 8975 # Using PORT 8975.
SERVER = "172.17.0.3" # Getting OUR server IP.
ADDR = (SERVER,PORT) # This should be a tuple.
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"

def timeX():
    """
    Time Function that gets the system time.
    Args: None
    Returns: Minute and Time.
    """
    t = time.localtime()
    current_minute = time.strftime("%M", t)
    current_time = time.strftime("%H:%M:%S", t)
    return current_minute, current_time # Tuple

def start():
    """
    Start new connections and then send to client_handling.
    """
    server.listen() # To start listening for new connections.

    print(f"[LISTENING] Server is listening on {SERVER}")
    # Starting an infinate loop.
    while True:
        """
        Wait for new connections to the server.
        Upon new connection a new socket object is returned representing
        the connection, and a tuple holding the address of the client that
        is (host, port) <- FOR IPv4!
        """
        connection, address = server.accept()
        # New Socket object to accept new connections from clients.
        # Starting a Thread to handle each client.
        thread = threading.Thread(target=client_handling, args=(connection,\
            address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1 }")
        # -1 to eliminate the current script's thread.  

def client_handling(connection, address):
    """
    Client handling, This function will handle individual connections
    1 client and 1 server.
    """
    ping_interval = []
    print(f"[TIME:] {timeX()[1]} [NEW CONNECTION] {address} connected.")
    with open("clientlogs.txt", "a+") as x:
        x.write(f"[TIME:] {timeX()[1]} [NEW CONNECTION] {address} connected.")

    connected = True
    while connected:
        """
        Our logic here is to receive the length of the msg that is going to 
        come first so that we know what size of msg we need to make provision
        first. 
        .decode -> from byte format to str (utf-8 for now).
        """
        msg_length = connection.recv(HEADER).decode(FORMAT)
        # The first message from the server won't be a valid one!
        # So we need to stablish a test.
        if msg_length: # Tf this is not NONE:
            msg_length = int(msg_length)
            msg = connection.recv(msg_length).decode(FORMAT)
            """
            Handling Clean Disconnection so that we can handle re-
            connection of any client.
            """
            if msg == "!PING":
                #print(msg)
                ping_interval.append(int(timeX()[0]))
                # to handle size of list.
                if len(ping_interval) > 5:
                    ping_interval.pop(0)

            if msg == DISCONNECT_MSG:
                connected = False # Loop is now closed.
            if msg != DISCONNECT_MSG and msg != "!PING":
                logFile = open("clientlogs.txt", "a+")
                logFile.write(f"[TIME:] {timeX()[1]} [{address}] {msg}\n")
                logFile.close()
                print(f"[TIME:] {timeX()[1]} [{address}] {msg}")
                # Server sending msg to the client.
                # connection.send("Msg received".encode(FORMAT))
        else:
            try:
                if int(timeX()[0]) - ping_interval[-1] > 5:
                    print(f"Lost {address}: Disconnecting")
                    logFile = open("clientlogs.txt", "a+")
                    logFile.write(f"[TIME:] {timeX()[1]} [{address}] No ping \
                    for 5 min. Disconnecting... \n")
                    logFile.close()
                    connected = False
                else:
                    connected = True
            except IndexError:
                print("Client could not send ping messages to handle clean \
                disconnection.")
                print("Try starting client again!")
                with open("clientlogs.txt", "a+") as write:
                    write.write("Client could not send ping messages to handle \
                        clean disconnection.")
                connected = False
    connection.close()

def main():
    print("[STARTING] Server is starting...")
    start()

if __name__=="__main__":
    try:
        pid = os.fork()
        if pid > 0:
            # Exitting parent process
            sys.exit(0)
    except OSError:
        servLog = open("serverlogging.txt", "a+")
        servLog.write(f"[TIME:] {timeX()[1]} OS Error!\n Exiting.")
        servLog.close()
        sys.exit(1)

    # Creating a socket. Using IPv4.
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # Binding to our IP and Port to allow listening to incoming requests to 
    # that IP and port.
    server.bind(ADDR) # Expcts a tuple.
    main()
