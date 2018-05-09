import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets
from Demo import Classification

inputFile = ""
openSmilePath = "/Users/xwy/Downloads/openSMILE-2.1.0/"
smileExtract = openSmilePath+"inst/bin/SMILExtract"
configPath = "./IS10_paraling_2.conf"

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
        self.open_filename, self.open_filetype = QFileDialog.getOpenFileName(self, "Open a MP3 file", "/", "MP3 (*.mp3)")
        print(self.open_filename)
        if(self.open_filename):
            if(os.path.exists("out.csv")):
                os.remove("out.csv")
            if(os.path.exists("out.wav")):
                os.remove("out.wav")
            ret = os.system("ffmpeg -i "+self.open_filename+" -vn out.wav &> info.txt")
            os.system(smileExtract+" -C "+configPath+" -I out.wav -O out.csv &> info.txt")
            c = Classification("out.csv")
            res = c.run()
            if(res == 1):
                self.lcdNumber_2.display(c.valance*10)
                self.lcdNumber.display(c.arousal*10)
        pass

    def click_generate(self):
        self.save_filename, self.save_filetype = QFileDialog.getSaveFileName(self, "Save a MIDI file", "/", "MIDI (*.mid);")
        print(self.save_filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWindow()
    widget.show()
    sys.exit(app.exec_())
