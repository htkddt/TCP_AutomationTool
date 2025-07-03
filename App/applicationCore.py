import os
import sys
import socket
import json

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

        self.socket = TCPSocket()
        self.socket.connectFinished.connect(self.initData)

        self.uic.btnConDis.clicked.connect(self.establishConnectAct)
        self.uic.btnOK.clicked.connect(self.runAct)
        self.uic.btnCancel.clicked.connect(self.clearSelection)

    def establishConnectAct(self):
        if self.uic.btnConDis.text() == "Connect to server":
            self.uic.btnConDis.setText("Disconnect to server")

            HOST = self.uic.txtHOST.text()
            Port = int(self.uic.txtPort.text())

            self.socket.serverAddress(HOST, Port)
            self.socket.status = 0
            self.socket.start()

        elif self.uic.btnConDis.text() == "Disconnect to server":
            self.uic.btnConDis.setText("Connect to server")
            sendData = {
                "argv":"client",
                "value":"stop"
            }
            self.socket.send_function(sendData)
            self.uic.txtTicket.clear()
            if (self.uic.cBoxBuildVersions.count() > 0): self.uic.cBoxBuildVersions.clear()
            for i in range(self.uic.layoutTestSuites.count()):
                item = self.uic.layoutTestSuites.itemAt(i)
                widget = item.widget()
                if isinstance(widget, QCheckBox):
                    self.uic.layoutTestSuites.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
            self.clearCheckedItems(self.uic.layoutReports)
            self.socket.disconnect()

    def initData(self, connected):
        if not connected: return
        sendData = {
            "argv":"server",
            "value":"init"
        }
        self.socket.send_function(sendData)

        recvData = self.socket.received_function()
        buildVersions = recvData["build-version"]
        for build in buildVersions:
            self.uic.cBoxBuildVersions.addItem(build)

        testSuites = recvData["test-suites"]
        for test in testSuites:
            checkbox = QCheckBox(test)
            self.uic.layoutTestSuites.addWidget(checkbox)
        self.uic.layoutTestSuites.addStretch()

    def runAct(self):
        sendData = {
                "ticket-id":self.uic.txtTicket.text(),
                "build-version-name":self.uic.cBoxBuildVersions.currentText(),
                "build-version-size":"0",
                "test-suites":self.getCheckedItems(self.uic.layoutTestSuites),
                "time":[self.uic.txtTime.text(), self.uic.txtDate.text()],
                "reports":self.getCheckedItems(self.uic.layoutReports)
            }
        print(json.dumps(sendData, indent=2))
        self.socket.send_function(sendData)
    
    def getCheckedItems(self, obj):
        checked = []
        for i in range(obj.count() - 1):
            checkbox = obj.itemAt(i).widget()
            if checkbox.isChecked():
                checked.append(checkbox.text())
        return checked

    def clearCheckedItems(self, obj):
        for i in range(obj.count() - 1):
            checkbox = obj.itemAt(i).widget()
            if checkbox.isChecked(): checkbox.setChecked(False)

    def clearSelection(self):
        self.uic.txtTicket.clear()
        self.clearCheckedItems(self.uic.layoutTestSuites)
        self.clearCheckedItems(self.uic.layoutReports)


class TCPSocket(QThread):
    connectFinished = pyqtSignal(bool)
    def __init__(self):
        super(TCPSocket, self).__init__()
        self.HOST = ''
        self.Port = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("TCPSocket thread Finished Init")

    def run(self):
        try:
            self.s.connect((self.HOST, self.Port))
            print("Connection is established...")
            print("------------------------------------------")
            self.connected = True
        except Exception as e:
            self.connected = False
            print("Error:", e)
        self.connectFinished.emit(self.connected)

    def disconnect(self):
        if self.s:
            self.s.close()
            self.connected = False
            print("Disconnected")
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def serverAddress(self, HOST, Port):
        self.HOST = HOST
        self.Port = Port

    def send_function(self, sendData):
        sendJSON = json.dumps(sendData)
        self.s.sendall((sendJSON + "\n").encode())

    def received_function(self):
        recvJSON = ""
        while not recvJSON.endswith("\n"):
            recvJSON += self.s.recv(1).decode()
        try:
            recvData = json.loads(recvJSON.strip())
        except json.JSONDecodeError as e:
            print("Error: ", e)
        return recvData


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setMinimumSize(400, 600)
    window.showMinimized()
    sys.exit(app.exec())