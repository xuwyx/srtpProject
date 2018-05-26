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
from midiModify import MidiModify

inputFile = ""
openSmilePath = "/Users/xwy/Downloads/openSMILE-2.1.0/"
smileExtract = openSmilePath + "inst/bin/SMILExtract"
configPath = "./IS10_paraling_2.conf"

class genThread(QThread):
    gslot = pyqtSignal(int)

    def __init__(self, file_name, v, a):
        super(genThread, self).__init__()
        self.file_name = file_name
        self.v = v
        self.a = a

    def run(self):
        g = Generation('out.mid', self.v, self.a)
        self.gslot[int].emit(1)
        # g.calculate(self.v, self.a)

        self.gslot[int].emit(2)
        g.sample()
        self.gslot[int].emit(3)
        g.deal_abc()
        self.gslot[int].emit(4)
        m = MidiModify(self.file_name, self.v, self.a, g.bpm)
        self.gslot[int].emit(5)
        res = m.dealing()
        if res is False:
            self.gslot[int].emit(8)
            return

        self.gslot[int].emit(6)
        p = os.getcwd()
        # os.remove(p + '/out.mid')
        self.gslot[int].emit(7)



class musicThread(QThread):
    mslot = pyqtSignal(int, int)

    def __init__(self):
        super(musicThread, self).__init__()

    def run(self):
        print('thread %s is running...' % threading.current_thread().name)
        pygame.mixer.init()
        track = pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        # pygame.mixer.music.fadeout(250000)
        if song:
            print("ffmpeg...")
            if os.path.exists("out.csv"):
                os.remove("out.csv")
            if os.path.exists("out.wav"):
                os.remove("out.wav")
            ret = os.system("ffmpeg -i " + song + " -vn out.wav &> info.txt")
            print("openSmile...")
            os.system(smileExtract + " -C " + configPath + " -I out.wav -O out.csv &> info.txt")
            print("machine learning...")
            c = Classification("out.csv")
            res = c.run()
            if res == 1:
                self.mslot[int, int].emit(c.valance * 10, c.arousal * 10)
            print('thread %s ended.' % threading.current_thread().name)
        pass

# def playMusic():
#     print('thread %s is running...' % threading.current_thread().name)
#     pygame.mixer.init()
#     track = pygame.mixer.music.load(song)
#     if song:
#         if os.path.exists("out.csv"):
#             os.remove("out.csv")
#         if os.path.exists("out.wav"):
#             os.remove("out.wav")
#         print("ffmpeg...")
#         ret = os.system("ffmpeg -i " + song + " -vn out.wav &> info.txt")
#         print("openSmile...")
#         os.system(smileExtract + " -C " + configPath + " -I out.wav -O out.csv &> info.txt")
#         c = Classification("out.csv")
#         print("machine learning...")
#         res = c.run()
#         print('thread %s ended.' % threading.current_thread().name)
#     pass
#     #
#     # num = int(self.edit.text())
#     progress = QProgressDialog()
#     progress.setWindowTitle("请稍等")
#     progress.setLabelText("正在播放所选音乐...")
#     progress.setCancelButtonText("取消")
#     progress.setMinimumDuration(5)
#     progress.setWindowModality(Qt.WindowModal)
#     progress.setRange(0, 300)
#     progress.show()
#     for i in range(300):
#         progress.setValue(i)
#         if progress.wasCanceled():
#             # QMessageBox.warning(self, "提示", "操作失败")
#             break
#         else:
#             progress.setValue(i)
#             # QMessageBox.information("提示", "操作成功")
#     pygame.mixer.music.play()
#     pygame.mixer.music.fadeout(90000)


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
        # self.cancelBtn = QPushButton("OK")

        # musicThread.mslot[int, int].connect('self.calculate_done')

    def click_recognize(self):
        self.open_filename, self.open_filetype = QFileDialog.getOpenFileName(self, "Open a MP3 file", "/",
                                                                             "MP3 (*.mp3)")
        print(self.open_filename)
        if(self.open_filename):
            global song
            song = self.open_filename
            print('thread %s is running...' % threading.current_thread().name)

        # t = threading.Thread(target=playMusic)
            t = musicThread()
            t.mslot[int, int].connect(self.calculate_done)
            t.start()
            self.progress = QProgressDialog()
            self.progress.setWindowTitle("请稍等")
            self.progress.setMinimumWidth(400)
            self.progress.setLabelText("正在分析所选音乐...")
        # self.cancelBtn.setDisabled(True)
        # self.progress.setCancelButton(self.cancelBtn)
            self.progress.setCancelButtonText("OK")
            self.progress.setAutoClose(False)
            self.progress.setDisabled(True)
            self.progress.setMinimumDuration(1)
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setRange(0, 10000000)
            for i in range(10000000):
                self.progress.setValue(i)
                if self.progress.wasCanceled():
                    pygame.mixer.music.stop()
                    t.terminate()
                    t.wait()
                # QMessageBox.warning(self, "提示", "操作失败")
                    break
                else:
                    self.progress.setValue(i)
                # QMessageBox.information("提示", "操作成功")

    def calculate_done(self, l1, l2):
        self.lcdNumber_2.display(l1)
        self.lcdNumber.display(l2)
        # self.cancelBtn.setDisabled(False)
        self.progress.setLabelText("分析完成 单击按钮停止播放音乐")
        self.progress.setDisabled(False)

    def click_generate(self):
        self.save_filename, self.save_filetype = QFileDialog.getSaveFileName(self, "Save a MIDI file", "/",
                                                                             "MIDI (*.mid);")
        if self.save_filename:
            print(self.save_filename)
            self.m.btn.setFileName(self.save_filename)
            self.m.btn.set_va(0, 0, False)
            self.installEventFilter(self.m)
            self.m.setFocus()
            if self.m.exec_():
                print("ok")

    def eventFilter(self, source, event):
        if source == self.m.btn:
            if event.type() == QEvent.MouseMove:
                pos = event.pos()
                if  68<pos.x()<408 and 77<pos.y()<417:
                    x = (pos.x() - 238.0) / 34.0
                    y = - (pos.y() - 247.0) / 34.0
                    self.m.vtxt.setText('%f' % x)
                    self.m.atxt.setText('%f' % y)
                    self.m.btn.set_va(x, y, True)
                else:
                    self.m.vtxt.setText('')
                    self.m.atxt.setText('')
                    self.m.btn.set_va(0, 0, False)

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
        self.btn.finishSlot[bool].connect(self.finish)

    def finish(self, res):
        self.close()
        if res is False:
            QMessageBox.warning(self, 'Error', '生成失败，文件无权限写入', QMessageBox.Cancel, QMessageBox.Cancel)
            return
        reply = QMessageBox.question(self, 'Success', '生成完成，是否播放音乐？', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            pygame.mixer.init()
            track = pygame.mixer.music.load(genSong)
            pygame.mixer.music.play()
            reply2 = QMessageBox.information(self, 'Playing...', "播放音乐中...", QMessageBox.Cancel, QMessageBox.Cancel)
            if reply2 == QMessageBox.Cancel:
                pygame.mixer.music.stop()



class VAButton(QPushButton):
    finishSlot = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(VAButton, self).__init__(parent)
        self.file_name = ""
        self.hovered = False
        self.pressed = False
        self.pixmap = QPixmap("va.png")
        self.roundness = 0
        rect = QRect()
        rect.setWidth(500)
        rect.setHeight(500)
        self.setGeometry(rect)
        self.setFixedSize(QSize(500, 500))
        self.setIconSize(QSize(500, 500))
        self.v = 0
        self.a = 0
        self.ok = False

    def set_va(self, v, a, ok):
        self.v = v
        self.a = a
        self.ok = ok

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

    def process(self, p):
        if p == 8:
            self.progress.setValue(7)
            self.finishSlot[bool].emit(False)
            return
        self.progress.setValue(p)
        if p == 7:
            # self.progress.setDisabled(False)
            # self.progress.setLabelText("生成成功！")
            global genSong
            genSong = self.file_name
            self.finishSlot[bool].emit(True)

    def mousePressEvent(self, event):
        if self.ok is False:
            return
        self.pressed = True
        self.repaint()
        # self.g.setFileName(self.file_name)
        # self.g.calculate(self.v+5, self.a+5)
        # self.g.sample()
        # self.g.deal_abc()
        # m = MidiModify(self.file_name, self.v+5, self.a+5)
        # m.dealing()
        # p = os.getcwd()
        # os.remove(p+'/out.mid')
        QPushButton.mousePressEvent(self, event)
        # print("OK?", self.ok)
        t = genThread(self.file_name, self.v+5, self.a+5)
        t.gslot[int].connect(self.process)
        t.start()
        self.progress = QProgressDialog()
        self.progress.setWindowTitle("请稍等")
        self.progress.setMinimumWidth(400)
        self.progress.setLabelText("正在生成音乐...")
        # self.progress.setAutoClose(False)
        # self.cancelBtn.setDisabled(True)
        # self.progress.setCancelButton(self.cancelBtn)
        # self.progress.setCancelButtonText("OK")
        # self.progress.setDisabled(True)
        self.progress.setMinimumDuration(1)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setRange(0, 7)
        self.progress.setValue(0)




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
