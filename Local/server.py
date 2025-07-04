import os
import socket
import subprocess
import platform
import json

platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()

buildDir = f"C:\\Users\\tuanng4x\\Workspace\\SVN\\"
testDir = f"C:\\Users\\tuanng4x\\Workspace\\Tickets\\"

HOST = '127.0.0.1'
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Server listenning [{HOST}:{PORT}]...")
    while True:
        conn, addr = s.accept()
        print(f"Connected from {addr}")
        print("------------------------------------------")
        connected = True
        while True:
            recvJSON = ""
            while not recvJSON.endswith("\n"):
                recvJSON += conn.recv(1).decode()
            if recvJSON:
                try:
                    recvData = json.loads(recvJSON.strip())
                except json.JSONDecodeError as e:
                    print(e)
                if len(recvData) == 2:
                    if recvData["argv"] == "server":
                        if recvData["value"] == "init":
                            # print("Collect available data for client")
                            files = [os.path.splitext(name)[0] for name in os.listdir(buildDir) 
                                       if os.path.isfile(os.path.join(buildDir, name)) and name.endswith('.exe')]
                            folders = [name for name in os.listdir(testDir) 
                                       if os.path.isdir(os.path.join(testDir, name)) and not name.startswith('.')]
                            sendData = {
                                "argv":"client",
                                "value": {
                                    "build-version":files,
                                    "test-suites":folders
                                }
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            # print("------------------------------------------")
                            continue
                        elif recvData["value"] == "close" or recvData["value"] == "stop":
                            sendData = {
                                "argv":"client",
                                "value":"disconnected"
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            if recvData["value"] == "close":
                                print("Server was disconnected by user")
                                connected = False
                                break
                            if recvData["value"] == "stop":
                                print(f"Server listenning [{HOST}:{PORT}]...")
                                break
                    else:
                        print("ERROR: Incorrect request from client\nTo disconnect type: server stop or client stop")
                        print("------------------------------------------")
                        continue
                else:
                    ticket = recvData["ticket-id"]
                    buildName = recvData["build-version-name"] + ".exe"
                    buildSize = int(recvData["build-version-size"])
                    if buildSize != 0:
                        destPath = os.path.join(buildDir, buildName)
                        with open(destPath, 'wb') as f:
                            size = 0
                            while size < buildSize:
                                bin = conn.recv(min(4096, buildSize - size))
                                if not bin:
                                    break
                                f.write(bin)
                                size += len(bin)
                    testSuites = recvData["test-suites"]
                    time = recvData["time"]
                    reports = recvData["reports"]
                    cmdPARA = {
                        "ticket-id":ticket,
                        "build-version-name":buildName,
                        "test-suites":testSuites,
                        "time":time,
                        "reports":reports
                    }
                    cmdJSON = json.dumps(cmdPARA)
                    cmd = f"python in-run_tst.py {ticket} bdd_test"
                    sendData = {
                        "argv":"status",
                        "value":"running"
                    }
                    sendJSON = json.dumps(sendData)
                    conn.sendall((sendJSON + "\n").encode())
                    print("Running in-run_tst.py...")
                    try:
                        if os_system == platforms["Linux"]:
                            process = subprocess.run(cmd.split(), input=cmdJSON.encode())
                        else:
                            process = subprocess.run(cmd.split(), shell=True, input=cmdJSON.encode())
                    except Exception as error:
                        print("Error: " + error)
                    if conn:
                        sendData = {
                            "argv":"status",
                            "value":"finished"
                        }
                        sendJSON = json.dumps(sendData)
                        conn.sendall((sendJSON + "\n").encode())
                    print("Finished.")
                    print("Run automation successful.")
                    print("------------------------------------------")
        if not connected: break