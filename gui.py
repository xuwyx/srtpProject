import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets
from Demo import Classification
from PyQt5.QtGui import *
from sample import Generation
# import pyglet
import time, threading
import pygame

inputFile = ""
openSmilePath = "/Users/xwy/Downloads/openSMILE-2.1.0/"
smileExtract = openSmilePath + "inst/bin/SMILExtract"
configPath = "./IS10_paraling_2.conf"


def playMusic():
    print('thread %s is running...' % threading.current_thread().name)

    pygame.mixer.init()
    track = pygame.mixer.music.load(song)
    pygame.mixer.music.play()
    pygame.mixer.music.fadeout(90000)


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.temp_count = 0
        self.timeout = 10
        self.open_filename = ""
        self.open_filetype = ""
        self.save_filename = ""
        self.save_filetype = ""
        self.m = MultiInPutDialog()
        self.m.btn.installEventFilter(self)

    def click_recognize(self):
        self.open_filename, self.open_filetype = QFileDialog.getOpenFileName(self, "Open a MP3 file", "/",
                                                                             "MP3 (*.mp3)")
        print(self.open_filename)
        global song
        song = self.open_filename
        print('thread %s is running...' % threading.current_thread().name)
        t = threading.Thread(target=playMusic)
        t.start()
        if self.open_filename:
            if os.path.exists("out.csv"):
                os.remove("out.csv")
            if os.path.exists("out.wav"):
                os.remove("out.wav")
            ret = os.system("ffmpeg -i " + self.open_filename + " -vn out.wav &> info.txt")
            os.system(smileExtract + " -C " + configPath + " -I out.wav -O out.csv &> info.txt")
            c = Classification("out.csv")

            res = c.run()
            if (res == 1):
                self.lcdNumber_2.display(c.valance * 10)
                self.lcdNumber.display(c.arousal * 10)
            t.join()
            print('thread %s ended.' % threading.current_thread().name)
        pass


    def click_generate(self):
        self.save_filename, self.save_filetype = QFileDialog.getSaveFileName(self, "Save a MIDI file", "/",
                                                                             "MIDI (*.mid);")
        print(self.save_filename)
        self.m.btn.setFileName(self.save_filename)
        self.installEventFilter(self.m)
        self.m.setFocus()
        if self.m.exec_():
            print("ok")

    def eventFilter(self, source, event):
        if source == self.m.btn:
            if event.type() == QEvent.MouseMove:
                pos = event.pos()
                self.m.vtxt.setText('%d' % pos.x())
                self.m.atxt.setText('%d' % pos.y())
                # self.setCursor(Qt.UpArrowCursor)
        #     else:
        #         self.setCursor(Qt.ArrowCursor)
        # else:
        #     self.setCursor(Qt.ArrowCursor)
        return QMainWindow.eventFilter(self,  source,  event)


class MultiInPutDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.resize(500, 600)
        self.setWindowTitle('Set V-A Value')
        self.btn = VAButton()
        layout = QVBoxLayout()
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btn)
        layout.addStretch()
        layout.addItem(btnLayout)
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Valence:"))
        self.vtxt = QLabel()
        hlayout.addWidget(self.vtxt)
        hlayout.addWidget(QLabel("Arousal:"))
        self.atxt = QLabel()
        hlayout.addWidget(self.atxt)
        layout.addStretch()
        layout.addItem(hlayout)
        layout.addStretch()
        self.setLayout(layout)


class VAButton(QPushButton):
    def __init__(self, parent=None):
        super(VAButton, self).__init__(parent)
        self.file_name = ""
        self.hovered = False
        self.pressed = False
        self.pixmap = QPixmap("va.png")
        self.roundness = 0
        rect = QRect()
        rect.setWidth(300)
        rect.setHeight(300)
        self.setGeometry(rect)
        self.setFixedSize(QSize(300, 300))
        self.setIconSize(QSize(300, 300))
        self.g = Generation(self.file_name, 1, 1)

    def setFileName(self, file_name):
        self.file_name = file_name

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        button_rect = QRect(self.geometry())
        # button_rect.setSize(QSize(100, 100))
        painter.setPen(QPen(QBrush(Qt.red), 2.0))
        painter_path = QPainterPath()
        painter_path.addRoundedRect(1, 1, button_rect.width() - 2, button_rect.height() - 2, self.roundness,
                                    self.roundness)
        painter.setClipPath(painter_path)
        if self.isEnabled():
            icon_size = self.iconSize()
            icon_position = self.calculateIconPosition(button_rect, icon_size)
            painter.setOpacity(1.0)
            # painter.drawRect(icon_position)
            painter.drawPixmap(icon_position, self.pixmap)

    def enterEvent(self, event):
        self.hovered = True
        self.repaint()
        QPushButton.enterEvent(self, event)

    def leaveEvent(self, event):
        self.hovered = False
        self.repaint()
        QPushButton.leaveEvent(self, event)

    def mousePressEvent(self, event):
        self.pressed = True
        self.repaint()
        self.g.setFileName(self.file_name)
        self.g.calculate()
        self.g.sample()
        self.g.deal_abc()
        QPushButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.repaint()
        QPushButton.mouseReleaseEvent(self, event)

    def calculateIconPosition(self, button_rect, icon_size):
        x = (button_rect.width() / 2) - (icon_size.width() / 2)
        y = (button_rect.height() / 2) - (icon_size.height() / 2)
        width = icon_size.width()
        height = icon_size.height()
        icon_position = QRect()
        icon_position.setX(x)
        icon_position.setY(y)
        icon_position.setWidth(width)
        icon_position.setHeight(height)
        return icon_position




if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWindow()
    widget.show()
    app.installEventFilter(widget)

    sys.exit(app.exec_())
