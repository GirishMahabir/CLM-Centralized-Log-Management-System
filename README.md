# CLM (Centralized Log Management)
CLIENT-SERVER Architecture where there is a CENTRAL server to which multiple clients sends their LOGS to.

# Getting Started

## Pre-Requisite:
- Python3
    ```
    sudo apt-get install python3
    ```
## Client-Side Script
Getting the client-side script ready.
```python
SERVER = "X.X.X.X" # Replace the x.x.x.x with the Server IP.
LOCALIP = "y.y.y.y" # Replace the y.y.y.y with your Local IP.

# Add in all the files you want to READ FROM in:

FilesToMonitor = ["[PATH 1]", "[PATH 2]"]  # separated by comma (,).

# ALLOWED PORTS:
ALLOW = [22,3306]

# If you want scanning on, Change:

SCANNING = True # STILL ON TESTING! GETTING FALSE POSITIVES!
```

## Server-Side Script
Getting the Server-side script ready.
```python
SERVER = "X.X.X.X" # Replace the x.x.x.x with the Server IP. LocalIP
```

# Running the scripts:
Make sure the port that is being used by these scripts are open!  
Default = 8975
## On Server:

```bash
python3 server_side.py
```
Note: The logs with be written in the same directory as: clientlogs.txt

- If there is no response from any client for 5 Minutes, the server will close the connection to it.

## On Client:
```
python3 client.py
```

# Scanning:

Along with the CLM System, It also consists of a realtime port scanning that runs on localhost of each client. Anytime a port that is not in the ALLOW list open up, the server will receive an Alert.

TESTING IN PROGRESS! GETTING FALSE POSITIVES!

# Testing:
- Deployed 2 VM's:

    ## Testing log feature!
    - Server:
        - IP: 192.168.100.214
        - Python3 installed.
        
    - Client:
        - IP: 192.168.100.215
        - Python3 installed.
        - ALLOWED ROOT SSH LOGIN.
        
        - Generate come logs or manually add tests to the file that is being monitored!
    
    ## Testing OPEN PORTS feature. Still in progress!
    - Locally:
        EDID THE hosts file in: Ansible/hosts, change to the [client_IP]
        ```bash
        $ docker build -t ansible-protect:latest .
        $ docker run -it --rm ansible-protect:latest bash
        $ ssh-keygen
        $ ssh-copy-id [client_IP]
        $ ansible main.yml
        $ exit

        $ cd ../OPEN
        
        CHECK THE hosts file again.

        $ docker build -t ansible-expose:latest .
        $ docker run -it --rm ansible-expose:latest bash
        $ ssh-keygen
        $ ssh-copy-id [client_IP]
        $ ansible main.yml
        $ exit
        ```
        Here we should get the open port alert on the server since we opened the port 10066, that is not in the Allowed List.
    