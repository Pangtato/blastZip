import queue
import threading

import pyzipper
from PyQt6.QtCore import pyqtSignal, QThread


class Unzip(QThread):
    """
        zip爆破
    """
    logSignal = pyqtSignal(str)
    findSignal = pyqtSignal(str)
    finishSignal = pyqtSignal()
    relPwd = None

    def __init__(self, filepath, pwdSeed, stopFlag):
        super(Unzip, self).__init__()
        self.filepath = filepath
        self.pwdSeed = pwdSeed
        self.stopFlag = stopFlag

    def runRar(self):
        try:
            while self.stopFlag == 0:
                try:
                    pwd = self.pwdqueue.get()
                    self.append(f'\r\n[线程{self.pwdSeed}]尝试使用{pwd}破解({self.pwdqueue.qsize()})...')
                    file = pyzipper.AESZipFile(self.filepath, 'r', compression=pyzipper.ZIP_DEFLATED,
                                               encryption=pyzipper.WZ_AES)
                    file.extractall(pwd=pwd.encode('utf8'))
                    self.stopFlag = 1
                    self.relPwd = pwd
                    self.append(f'\r\n[线程{self.pwdSeed}]破解成功，密码为：{pwd}')
                    self.findSignal.emit(pwd)
                    break
                except Exception as e:
                    self.append(f'\r\n[线程{self.pwdSeed}]解压失败,{e}')
        finally:
            self.finishSignal.emit()

    def append(self, text):
        print(text)
        self.logSignal.emit(text)

    def run(self):
        self.pwdqueue = queue.Queue(10000)
        threading.Thread(target=genPwd, args=(self.pwdqueue, self.pwdSeed)).start()
        self.runRar()

        if self.stopFlag == -1:
            self.logSignal.emit(f'[线程{self.pwdSeed}]程序已终止')


def genPwd(pwdqueue, pwdSeed):
    e = list(pwdSeed)
    for i in e:
        genPwd_(num=i, pwdqueue=pwdqueue)
        for j in e:
            genPwd_(num=j, pwdqueue=pwdqueue)


def genPwd_(num, pwdqueue):
    n = 0
    pwdqueue.put(num + str(n))
    while n < 1000:
        n = n + 1
        pwdqueue.put(num + str(n))
        pwdqueue.put(num.upper() + str(n))
