import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets

inputFile = ""


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.temp_count = 0
        self.open_filename = ""
        self.open_filetype = ""
        self.save_filename = ""
        self.save_filetype = ""

    def click_recognize(self):
        self.open_filename, self.open_filetype = QFileDialog.getOpenFileName(self, "Open a MP3 file", "/", "MP3 (*.mp3);")
        print(self.open_filename)
        self.temp_count += 1
        self.lcdNumber_2.display(self.temp_count)
        pass

    def click_generate(self):
        self.save_filename, self.save_filetype = QFileDialog.getSaveFileName(self, "Save a MIDI file", "/", "MIDI (*.mid);")
        print(self.save_filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWindow()
    widget.show()
    sys.exit(app.exec_())
