import os
import sys
import socket
import json
import threading

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QCheckBox

from applicationUI import MainWindowUI

EMAILS = ["sangx.phan@intel.com", "thex.do@intel.com", "tuanx.nguyen@intel.com", "maix.tan@intel.com", "taix.them@intel.com", "thinhx.le@intel.com"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = MainWindowUI()
        self.uic.initUI(self)

        for mail in EMAILS:
            checkbox = QCheckBox(mail)
            self.uic.layoutReports.addWidget(checkbox)
        self.uic.layoutReports.addStretch()

        self.socket = TCPSocketConnection()
        self.socket.connectFinished.connect(self.initData)
        self.socket.responseFinished.connect(self.serverResponseAct)

        self.uic.btnConDis.clicked.connect(self.establishConnectAct)
        self.uic.btnOK.clicked.connect(self.runAct)
        self.uic.btnCancel.clicked.connect(self.clearSelection)

    def establishConnectAct(self):
        if self.uic.btnConDis.text() == "Connect to server":
            self.uic.btnConDis.setText("Disconnect to server")

            HOST = self.uic.txtHOST.text()
            Port = int(self.uic.txtPort.text())

            self.socket.serverAddress(HOST, Port)
            self.socket.start()

        elif self.uic.btnConDis.text() == "Disconnect to server":
            self.uic.btnConDis.setText("Connect to server")
            sendData = {
                "argv":"server",
                "value":"stop"
            }
            self.socket.clientRequest(sendData)
            self.uic.txtTicket.clear()
            if (self.uic.cBoxBuildVersions.count() > 0): self.uic.cBoxBuildVersions.clear()
            for i in reversed(range(self.uic.layoutTestSuites.count())):
                checkbox = self.uic.layoutTestSuites.itemAt(i).widget()
                if isinstance(checkbox, QCheckBox):
                    self.uic.layoutTestSuites.removeWidget(checkbox)
                    checkbox.setParent(None)
                    checkbox.deleteLater()
            self.clearCheckedItems(self.uic.layoutReports)

    def initData(self, connected):
        if not connected: return
        sendData = {
            "argv":"server",
            "value":"init"
        }
        self.socket.clientRequest(sendData)

    def serverResponseAct(self, recvData):
        if (len(recvData) == 2):
            if recvData["argv"] == "client":
                if recvData["value"] == "disconnected":
                    self.socket.stop()
                elif recvData["value"] == "finished":
                    self.uic.btnOK.setEnabled(True)
                    self.uic.btnCancel.setEnabled(True)
                    self.uic.btnConDis.setEnabled(True)
                else:
                    buildVersions = recvData["value"]["build-version"]
                    for build in buildVersions:
                        self.uic.cBoxBuildVersions.addItem(build)
                    testSuites = recvData["value"]["test-suites"]
                    for test in testSuites:
                        checkbox = QCheckBox(test)
                        self.uic.layoutTestSuites.addWidget(checkbox)
                    self.uic.layoutTestSuites.addStretch()
            elif recvData["argv"] == "status":
                if recvData["value"] == "running":
                    self.uic.btnOK.setEnabled(False)
                    self.uic.btnCancel.setEnabled(False)
                    self.uic.btnConDis.setEnabled(False)
                elif recvData["value"] == "finished":
                    self.uic.btnOK.setEnabled(True)
                    self.uic.btnCancel.setEnabled(True)
                    self.uic.btnConDis.setEnabled(True)

    def runAct(self):
        ticket = self.uic.txtTicket.text()
        test = self.getCheckedItems(self.uic.layoutTestSuites)
        time = [self.uic.txtTime.text(), self.uic.txtDate.text()]
        reports = self.getCheckedItems(self.uic.layoutReports)
        if (ticket == "") or (len(test) == 0) or (len(reports) == 0): return
        sendData = {
            "ticket-id":ticket,
            "build-version-name":self.uic.cBoxBuildVersions.currentText(),
            "build-version-size":"0",
            "test-suites":test,
            "time":time,
            "reports":reports
        }
        self.socket.clientRequest(sendData)
    
    def getCheckedItems(self, obj):
        checked = []
        for i in range(obj.count() - 1):
            checkbox = obj.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox):
                if checkbox.isChecked():
                    checked.append(checkbox.text())
        return checked

    def clearCheckedItems(self, obj):
        for i in range(obj.count() - 1):
            checkbox = obj.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox):
                if checkbox.isChecked(): 
                    checkbox.setChecked(False)

    def clearSelection(self):
        self.uic.txtTicket.clear()
        self.clearCheckedItems(self.uic.layoutTestSuites)
        self.clearCheckedItems(self.uic.layoutReports)


class TCPSocketConnection(QThread):
    connectFinished = pyqtSignal(bool)
    responseFinished = pyqtSignal(dict)
    def __init__(self):
        super(TCPSocketConnection, self).__init__()
        self.HOST = ''
        self.Port = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("TCPSocket thread Finished Init")

    def run(self):
        try:
            self.socket.connect((self.HOST, self.Port))
            print("Connection is established...")
            print("------------------------------------------")
            self.connected = True
            self.receiver = TCPSocketReceiver(self.socket)
            self.receiver.start()
            self.receiver.response.connect(self.serverResponse)
        except Exception as e:
            self.connected = False
            print("Error:", e)
        self.connectFinished.emit(self.connected)

    def stop(self):
        if self.receiver:
            self.receiver.stop()

        if self.socket:
            self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        print("Disconnected")

    def serverAddress(self, HOST, Port):
        self.HOST = HOST
        self.Port = Port

    def clientRequest(self, sendData):
        sendJSON = json.dumps(sendData)
        self.socket.sendall((sendJSON + "\n").encode())

    def serverResponse(self, recvJSON):
        recvData = json.loads(recvJSON.strip())
        self.responseFinished.emit(recvData)


class TCPSocketReceiver(QThread):
    response = pyqtSignal(str)
    def __init__(self, socket):
        super(TCPSocketReceiver, self).__init__()
        self.socket = socket
        self.running = True

    def run(self):
        while self.running:
            try:
                recvJSON = ""
                while not recvJSON.endswith("\n"):
                    recvJSON += self.socket.recv(1).decode()
                if recvJSON:
                    self.response.emit(recvJSON)
                else:
                    break
            except Exception as e:
                pass
                break
    
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
        print("TCPSocketReceiver is close")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setMinimumSize(400, 600)
    window.showMinimized()
    sys.exit(app.exec())