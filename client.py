import sys
import os
import socket
import json

# Release: pyinstaller --onefile --noconsole --name TCPAutomation --icon=nsicon.ico --distpath=. ./App/applicationCore.py
# Cmd: GUI-ID NocStudio 0 tst1|tst2|tst3 16:47 03/07/2025 sangx.phan@intel.com|thex.do@intel.com|tuanx.nguyen@intel.com
# Usage:
#   - python client.py local|remote|network
#   - server init
#   - server restart
#   - server stop

if len(sys.argv) < 2:
    print("Usage: python client.py [local|remote|network]")
    sys.exit(1)

if (sys.argv[1] == "local"): 
    HOST = '127.0.0.1'
    PORT = 9999
elif (sys.argv[1] == "network"):
    HOST = '127.0.0.1'
    PORT = 8888
elif (sys.argv[1] == "remote"): 
    HOST = '10.148.98.226'
    PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connection is established...")
    print("------------------------------------------")
    connected = True
    while True:
        msg = input().strip()
        if msg == "": continue
#--------------------------------------------------------------------------------
        msgSplit = msg.split(" ")
        if (msgSplit[0] == "server"):
            if msgSplit[1] != "init" and msgSplit[1] != "restart" and msgSplit[1] != "stop":
                print("ERROR: Incorrect request\nTo disconnect type: server restart|stop")
                print("------------------------------------------")
                continue
            sendData = {
                "argv":msgSplit[0],
                "value":msgSplit[1]
            }
        else:
            print("ERROR: Incorrect request")
            print("------------------------------------------")
            continue
            # sendData = {
            #     "ticket-id":msgSplit[0],
            #     "build-version-name":msgSplit[1],
            #     "build-version-size":msgSplit[2],
            #     "test-suites":msgSplit[3].split("|"),
            #     "schedule":[msgSplit[4], msgSplit[5]],
            #     "reports":msgSplit[6].split("|")
            # }
        sendJSON = json.dumps(sendData)
#--------------------------------------------------------------------------------
        s.sendall((sendJSON + "\n").encode())
        # if (len(msgSplit) == 6) and (msgSplit[2] != "0"):
        #     filePath = f"C:\\Users\\tuanng4x\\Workspace\\SVN\\{msgSplit[1]}.exe"
        #     with open(filePath, 'rb') as f:
        #         while True:
        #             bin = f.read(1024)
        #             if not bin:
        #                 break
        #             s.sendall(bin)
        print(json.dumps(sendData, indent=2))
        print("------------------------------------------")
        if msgSplit[0] == "server" and msgSplit[1] == "restart": break
        while True:
            recvJSON = ""
            while not recvJSON.endswith("\n"):
                recvJSON += s.recv(1).decode()
            if recvJSON:
                print("***Data received:")
                try:
                    recvData = json.loads(recvJSON.strip())
                    print(json.dumps(recvData, indent=2))
                except json.JSONDecodeError as e:
                    print(e)
                print("***Data details:")
                argv = recvData["argv"]
                value = recvData["value"]
                print(f"argv:\t{argv}")
                if recvData["argv"] == "client":
                    if recvData["value"] == "disconnected":
                        print(f"value:\t{value}")
                        connected = False
                    # elif recvData["value"] == "finished":
                    #     print(f"value:\t{value}")
                    elif recvData["value"] == "error":
                        print(f"value:\t{value}")
                    else:
                        buildVersions = recvData["value"]["build-version"]
                        testSuites = recvData["value"]["test-suites"]
                        print("value:\t")
                        print("\tBuild versions:")
                        for i in range(len(buildVersions)):
                            print(f"\t\t{buildVersions[i]}")
                        print("\tTest suites:")
                        for i in range(len(testSuites)):
                            print(f"\t\t{testSuites[i]}")
                # elif recvData["argv"] == "status":
                #     if recvData["value"] == "running":
                #         print(f"value:\t{value}")
                #         print("------------------------------------------")
                #         continue
                #     elif recvData["value"] == "finished":
                #         print(f"value:\t{value}")
                #     elif recvData["value"] == "successful":
                #         print(f"value:\t{value}")
                # elif recvData["argv"] == "updated":
                #     print(f"value:\t{value}")
                #     print("------------------------------------------")
                #     continue
                print("------------------------------------------")
            break
        if not connected: break