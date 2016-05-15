import gi
import logging

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from os import path

logger = logging.getLogger('PassPy.LoginView')

class LoginView(object):
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.setLayout()

    def setLayout(self):
        self.grid = Gtk.Grid()

        self.window.add(self.grid)

        self.logo = Gtk.Image(expand=True)
        self.logo.set_from_file(
            path.join(path.dirname(path.abspath(__file__)),
                      '../resources/logo128.png')
        )
        self.passwordEntry = Gtk.Entry(valign=1, xalign = 0.5)
        self.passwordEntry.set_visibility(False)
        self.passwordEntry.connect('activate', self.onEnter)

        self.grid.attach(Gtk.Label(expand=True), 1, 0, 3, 1)
        self.grid.attach(Gtk.Label(expand=True), 0, 1, 1, 1)
        self.grid.attach(Gtk.Label(expand=True), 0, 2, 1, 1)
        self.grid.attach(self.logo, 1, 1, 1, 1)
        self.grid.attach(self.passwordEntry, 1, 2, 1, 1)
        self.grid.attach(Gtk.Label(expand=True), 2, 1, 1, 1)
        self.grid.attach(Gtk.Label(expand=True), 2, 2, 1, 1)
        self.grid.attach(Gtk.Label(expand=True), 1, 3, 3, 1)

    def onEnter(self, entry):
        password = entry.get_text()
        if self.app.unlock(password):
            self.grid.destroy()
            self.window.mainView.unlock()
        else:
            entry.set_text('')
            logger.info('Wrong password provided')

        return True