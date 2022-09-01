import keyboard

from pynput.keyboard import Key, Listener

from PyQt5.QtCore import *

from PyQt5.QtCore import Qt

class myKeyboardMouse(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.isKeyMouse = False
        self.Key = None
        self.pressKey = None
        self.releaseKey = None

    def run(self):
        while self.isKeyMouse == True:
            # Collect events until released
            with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()


    def on_press(self, key):
        if self.pressKey != key:
            self.pressKey = key
            self.releaseKey = None
            print('{0} 누름'.format(key))

    def on_release(self, key):
        if self.releaseKey != key:
            self.releaseKey = key
            self.pressKey = None
            print('{0} 뗌'.format(key))
        if key == Key.esc:
            # Stop listener
            return False



