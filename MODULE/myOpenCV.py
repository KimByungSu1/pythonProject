import cv2
import win32con
import win32gui

from PyQt5.QtCore import QThread

class myOpenCV(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        pass

