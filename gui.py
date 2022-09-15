#-*- encoding: utf8 -*-
import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QThread, QObject, pyqtSignal
from cafe_crawler import Ui_MainWindow
from crawler import Naver


class Worker(QObject):
    progress = pyqtSignal(str) 
    process_type = "today"
    finished = pyqtSignal()
    naver_id = ""
    naver_pw = ""
    request_number = 0
    excel_name = ""
    def run(self):
        self.progress.emit("실행중....")
        self.naver = Naver()
        if self.process_type == None:
            return
        if not self.naver.login(self.naver_id, self.naver_pw):
            self.progress.emit("로그인 실패")
            return
        self.progress.emit("로그인 성공")
        if self.process_type == "today":
            self.progress.emit("오늘자 정보 가져오는중.....")
            if not self.naver.getToday():
                self.progress.emit("오늘자 정보 가져오기 실패")
                return
            self.progress.emit("오늘자 정보 가져오기 성공")
        elif self.process_type == "N":
            self.progress.emit(f"{self.request_number}명 가져오는중.....")
            err = self.naver.getN(int(self.request_number))
            if not err:
                self.progress.emit(f"{self.request_number}명 가져오기 실패")
                return
            self.progress.emit(f"{self.request_number}명 가져오기 성공")
        if not self.naver.saveExcel(self.excel_name):
            self.progress.emit("엑셀 저장 실패")
            return
        self.progress.emit("엑셀 저장 성공")
        self.naver.driver.quit()
        self.progress.emit("상태창")
        self.finished.emit()



class WindowClass(QMainWindow, Ui_MainWindow) :
    def __init__(self) :
        super().__init__()
        self.type = None
        self.setupUi(self)
        self.textBrowser.setText("상태창")
        self.run.clicked.connect(self.run_clicked)
        self.N_count.clicked.connect(self.N_radio_clicked)
        self.today.clicked.connect(self.today_radio_clicked)
    def run_clicked(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.process_type = self.type
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.progress_emited)
        self.worker.request_number = self.form_N.text()
        self.worker.process_type = self.type
        self.worker.excel_name = self.form_excel_name.text()
        self.worker.naver_id = self.form_id.text()
        self.worker.naver_pw = self.form_pw.text()
        self.thread.start()
        self.run.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.run.setEnabled(True)
        )

    def progress_emited(self, text):
        self.textBrowser.setText(text)
    def today_radio_clicked(self):
        self.type = "today"
        self.form_N.setReadOnly(True)
        self.form_N.setStyleSheet("border-style: outset;\n"
"border-width: 2px;\n"
"border-radius: 50px;\n"
"padding-left: 5px;\n"
"padding-right: 5px;\n"
"padding-top: 3px;\n"
"background-color: rgb(177, 177, 177);\n"
"padding-bottom: 3px;")

    def N_radio_clicked(self):
        self.type = "N"
        self.form_N.setReadOnly(False)
        self.form_N.setStyleSheet("border-style: outset;\n"
"border-width: 2px;\n"
"border-radius: 50px;\n"
"padding-left: 5px;\n"
"padding-right: 5px;\n"
"padding-top: 3px;\n"
"background-color: white;\n"
"padding-bottom: 3px;")


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
