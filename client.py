import sys
import os
import socket
import json

# Cmd: GUI-ID NocStudio 0 tst1|tst2|tst3 19|00|00|03|07|2025 mail1|mail2|mail3

if len(sys.argv) < 2:
    print("Usage: python client.py [local|remote]")
    sys.exit(1)

if (sys.argv[1] == "local"): HOST = '127.0.0.1'
elif (sys.argv[1] == "remote"): HOST = '10.148.98.226'
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connection is established...")
    print("------------------------------------------")
    while True:
        msg = input().strip()
        if msg == "": continue
#--------------------------------------------------------------------------------
        msgSplit = msg.split(" ")
        if len(msgSplit) < 6:
            if (msgSplit[0] != "server"):
                if msgSplit[1] != "init" and msgSplit[1] != "close" and msgSplit[1] != "stop":
                    print("ERROR: Incorrect request\nTo disconnect type: server close|stop")
                    print("------------------------------------------")
                    continue
            sendData = {
                "argv":msgSplit[0],
                "value":msgSplit[1]
            }
        else:
            sendData = {
                "ticket-id":msgSplit[0],
                "build-version-name":msgSplit[1],
                "build-version-size":msgSplit[2],
                "test-suites":msgSplit[3].split("|"),
                "time":msgSplit[4].split("|"),
                "reports":msgSplit[5].split("|")
            }
        sendJSON = json.dumps(sendData)
#--------------------------------------------------------------------------------
        s.sendall((sendJSON + "\n").encode())
        if msgSplit[0] == "server" and msgSplit[1] == "stop": break
        if (len(msgSplit) == 6) and (msgSplit[2] != "0"):
            filePath = f"C:\\Users\\tuanng4x\\Workspace\\SVN\\{msgSplit[1]}.exe"
            with open(filePath, 'rb') as f:
                while True:
                    bin = f.read(1024)
                    if not bin:
                        break
                    s.sendall(bin)
        print(json.dumps(sendData, indent=2))
        print("------------------------------------------")
        if msgSplit[0] == "server":
            if msgSplit[1] == "close": break
            elif msgSplit[1] == "init":
                while True:
                    recvJSON = ""
                    while not recvJSON.endswith("\n"):
                        recvJSON += s.recv(1).decode()
                    if recvJSON:
                        print("Data received:")
                        try:
                            recvData = json.loads(recvJSON.strip())
                            print(json.dumps(recvData, indent=2))
                        except json.JSONDecodeError as e:
                            print(e)
                        buildVersions = recvData["build-version"]
                        testSuites = recvData["test-suites"]
                        print("Build versions:")
                        for i in range(len(buildVersions)):
                            print(f"\t{buildVersions[i]}")
                        print("Test suites:")
                        for i in range(len(testSuites)):
                            print(f"\t{testSuites[i]}")
                    print("------------------------------------------")
                    break