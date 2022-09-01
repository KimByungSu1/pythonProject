import keyboard

from pynput.keyboard import Key, Listener

from PyQt5.QtCore import *

from PyQt5.QtCore import Qt

class myKeyboardMouse(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.isKeyMouse = False
        self.pressKey = None
        self.releaseKey = None

    def run(self):
        while self.isKeyMouse == True:
            # Collect events until released
            with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()
            pass

    def on_press(self, key):
        if self.pressKey != key:
            self.pressKey = key
            print('{0} pressed'.format(key))

    def on_release(self, key):
        if self.releaseKey != key:
            self.releaseKey = key
            print('{0} release'.format(key))
        if key == Key.esc:
            # Stop listener
            return False



