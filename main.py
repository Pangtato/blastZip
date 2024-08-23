import sys

from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QFileDialog, QTextEdit, QLabel

import unzip


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZIP爆破")
        self.resize(800, 600)
        self.uiInit()
        self.show()

    def uiInit(self):
        self.selectBtn = QPushButton("选择文件", self)
        self.selectBtn.resize(100, 30)
        self.selectBtn.clicked.connect(self.openFile)
        self.selectBtn.move(10, 5)

        self.doBtn = QPushButton("启动", self)
        self.doBtn.resize(100, 30)
        self.doBtn.clicked.connect(self.doIt)
        self.doBtn.move(110, 5)

        self.doBtn = QPushButton("终止", self)
        self.doBtn.resize(100, 30)
        self.doBtn.clicked.connect(self.stopIt)
        self.doBtn.move(210, 5)

        self.threadNumLabel = QLabel("线程数：", self)
        self.threadNumLabel.resize(50, 30)
        self.threadNumLabel.move(320, 5)

        self.threadNumText = QTextEdit(self)
        self.threadNumText.resize(100, 30)
        self.threadNumText.setText("26")
        self.threadNumText.move(360, 5)

        # 内容显示区
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.resize(self.width(), 550)
        self.textEdit.move(0, 40)

    def stopIt(self, num):
        num = num if num is not False else -1
        if hasattr(self, "threads") and self.threads is not None and len(self.threads) > 0:
            for thread in self.threads:
                thread.stopFlag = num
        else:
            self.textEdit.append("程序未开始")

    def openFile(self):
        self.filePath = QFileDialog.getOpenFileName(self, "打开文件", "", "*.zip")
        if self.filePath[0] != "":
            self.textEdit.append(f"破解文件路径: {self.filePath[0]}")
        else:
            self.textEdit.append("用户取消了文件选择")

    def doIt(self):
        if hasattr(self, "filePath") and self.filePath[0] != "":
            self.textEdit.append("开始破解...")

            self.threads = []
            # 破解线程
            num = self.threadNumText.toPlainText()
            if num is None or num == '':
                num = 1
            else:
                num = int(num)
            pwdSeed = 'abcdefghijklmnopqrstuvwxyz'
            if num <= 0:
                num = 1
            elif num > len(pwdSeed):
                num = len(pwdSeed)
            stopFlag = 0
            for i in range(num):
                ps = pwdSeed[i::num]
                ur = unzip.Unzip(self.filePath[0], ps, stopFlag)
                self.threads.append(ur)
                ur.start()

            for t in self.threads:
                t.logSignal.connect(self.writeLog)
                t.findSignal.connect(self.findPwdLog)
                t.finishSignal.connect(self.threadFinished)

            self.threadsCount = len(self.threads)
        else:
            self.textEdit.append("破解失败，请先选择文件！")

    def writeLog(self, text):
        self.textEdit.append(text)
        self.textEdit.repaint()

    def findPwdLog(self, text):
        self.stopIt(1)
        self.sucessText = text

    def threadFinished(self):
        self.threadsCount -= 1
        print(f"当前剩余线程数：{self.threadsCount}")
        if self.threadsCount <= 0:
            self.threads = []
        if self.threadsCount <= 0 and hasattr(self, "sucessText"):
            self.textEdit.append(f"===================破解成功，密码为：{self.sucessText}===================")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    sys.exit(app.exec())
