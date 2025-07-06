import os
import socket
import subprocess
import platform
import json
import time

platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()

#buildDir = f"C:\\Users\\tuanng4x\\Workspace\\SVN\\"
#testDir = f"C:\\Users\\tuanng4x\\Workspace\\Tickets\\"
buildDir = f"D:\\A_TerraLogic\\TTSApplication"
testDir = f"D:\\A_TerraLogic\\"

HOST = '127.0.0.1'
PORT = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
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
                            print("Collect available data for client")
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
                            print("------------------------------------------")
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
                            sendData = {
                                "argv":"client",
                                "value":"error"
                            }
                            sendJSON = json.dumps(sendData)
                            conn.sendall((sendJSON + "\n").encode())
                            continue
                    else:
                        sendData = {
                            "argv":"client",
                            "value":"error"
                        }
                        sendJSON = json.dumps(sendData)
                        conn.sendall((sendJSON + "\n").encode())
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
                    schedule = recvData["schedule"]
                    timeValue = schedule[0]
                    dateValue = schedule[1]
                    reports = recvData["reports"]
                    cmdPARA = {
                        "ticket-id":ticket,
                        "build-version-name":buildName,
                        "test-suites":testSuites,
                        "schedule":schedule,
                        "reports":reports
                    }
                    cmdJSON = json.dumps(cmdPARA)
                    #cmd = f"python in-run_tst.py bdd_test"
                    cmd = fr'''schtasks /create /tn "{ticket}" /tr "run.bat" /sc once /st {timeValue}'''
                    #cmd = fr'''schtasks /create /tn "RunSquishTest" /tr "D:\A_TerraLogic\TerraTool\TCPTool\Local\run.bat" /sc once /st {timeValue}'''
                    print(cmd)
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
                    # totalTestSuites = 500
                    # currentTestSuite = 0
                    # failedTestSuites = 0
                    # startTime = time.time()
                    # while currentTestSuite < totalTestSuites:
                    #     startTestTime = time.time()
                    #     try:
                    #         if os_system == platforms["Linux"]:
                    #             process = subprocess.run(cmd.split(), input=cmdJSON.encode())
                    #         else:
                    #             process = subprocess.run(cmd.split(), shell=True, input=cmdJSON.encode())
                    #     except Exception as error:
                    #         print("Error: " + error)
                    #         failedTestSuites += 1
                    #     print("=================================================================")
                    #     print("=====================Start Temporary Reports=====================")
                    #     print("=================================================================")
                    #     print(f"- Total Test Cases: {totalTestSuites}")
                    #     print(f"- Current Test Case: {currentTestSuite}")
                    #     print(f"- Total Test Time: {str(time.time() - startTestTime)}")
                    #     print(f"- Failed Test cases: {failedTestSuites}")
                    #     print("=================================================================")
                    #     print("======================End Temporary Reports======================")
                    #     print("=================================================================")
                    #     currentTestSuite += 1
                    #     if conn:
                    #         sendData = {
                    #             "argv":"processing",
                    #             "value":f"{currentTestSuite}"
                    #         }
                    #         sendJSON = json.dumps(sendData)
                    #         conn.sendall((sendJSON + "\n").encode())
                    #     else:
                    #         print("Error: Server not responding. Test case failed by Networking")
                    #         failedTestSuites += 1
                    #     time.sleep(5)
                    if conn:
                        sendData = {
                            "argv":"status",
                            "value":"finished"
                        }
                        sendJSON = json.dumps(sendData)
                        conn.sendall((sendJSON + "\n").encode())
                    else:
                        print("Error: Server not responding. Test case failed by Networking")
                    print("Finished.")
                    # print(f"Total Process Time: {str(time.time() - startTime)}")
                    print("Run automation successful.")
                    print("------------------------------------------")
        if not connected: break