import os
from PyQt5.QtCore import pyqtSignal, QThread, QTimer
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import QtGui
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import requests
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    download_progress = pyqtSignal(int)
    download_complete = QtCore.pyqtSignal()

    def __init__(self, url, file_path):
        super().__init__()
        self.url = url
        self.file_path = file_path

    def run(self):
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(self.file_path, "wb") as file:
            for data in response.iter_content(1024):
                downloaded_size += len(data)
                file.write(data)
                # 计算下载的百分比并发射信号
                progress = int((downloaded_size / total_size) * 100)
                self.download_progress.emit(progress)

        self.download_complete.emit()

class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/downloader.ui")
        self.ui.label_5.setPixmap(QtGui.QPixmap("./img/Logo.png"))
        self.save_path = self.ui.lineEdit_5
        self.choose_file = self.ui.pushButton_2
        self.choose_file.clicked.connect(self.slot_btn_chooseFile)
        # self.password = self.ui.lineEdit_2
        self.start = self.ui.pushButton
        self.start.clicked.connect(self.obtain_data)
        self.progressBar = self.ui.progressBar
        #self.progressBar = self.findChild(QtWidgets.QProgressBar, 'progressBar')
        self.year = self.ui.lineEdit
        self.month_select = self.ui.comboBox
        self.month_select.currentIndexChanged.connect(self.on_combobox_changed)
        self.day_select = self.ui.comboBox_2
        self.day_select.currentIndexChanged.connect(self.on_combobox_changed)
        # self.month = self.month_select.currentText()

        #self.month = self.combo1.currentText()
        #self.day = self.ui.lineEdit_3
        self.issue = self.ui.lineEdit_4
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

    def on_combobox_changed(self):
        # 获取当前选中项的文本
        self.month = self.month_select.currentText()
        self.day = self.day_select.currentText()
    def slot_btn_chooseFile(self):
        self.dir_choose = QFileDialog.getExistingDirectory(None,"选取文件夹","")

        if self.dir_choose == "":
            print("\n取消选择")

            return

        print("\n你选择的文件夹为:")
        print(self.dir_choose)
        self.save_path.setText(f'{self.dir_choose}')
        # print("文件筛选器类型: ",filetype)

    def obtain_data(self):
        url = f'http://audiocdn.economist.com/sites/default/files/AudioArchive/{self.year.text()}/{self.year.text()}{self.month}{self.day}/Issue_{self.issue.text()}_{self.year.text()}{self.month}{self.day}_The_Economist_Full_edition.zip'
        print(url)
        self.filename = url.split('/')[-1]
        self.final_path = os.path.join(self.dir_choose, self.filename)
        self.download_thread = DownloadThread(url, self.final_path)
        self.download_thread.download_progress.connect(self.progressBar.setValue)
        self.download_thread.download_complete.connect(self.on_download_complete)
        self.download_thread.start()

    def on_download_complete(self):
        QtWidgets.QMessageBox.information(self, "下载完成", "文件已成功下载！")

    def startProgress(self):
        # 启动或重置定时器（100毫秒间隔）
        self.timer.start(100)

    def update_progress(self, chunk_size):
        # update the progress bar
        self.current_value = self.progressBar.value()
        self.new_value = self.current_value + chunk_size
        self.progressBar.setValue(self.new_value)
        if self.new_value >= 100:
            self.timer.stop()




# define a class for downloading files


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MyWindow()
    # 展示窗口
    w.ui.show()

    sys.exit(app.exec_())