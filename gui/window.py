import gi
import logging

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from loginview import LoginView
from mainview import MainView

logger = logging.getLogger('PassPy.Window')

class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(
            self,
            title=app.APPLICATION_NAME,
            application=app,
            default_width=app.WIN_WIDTH,
            default_height=app.WIN_HEIGHT
        )
        self.set_icon_from_file(app.ICON)

        self.loginView = LoginView(app, self)
        self.mainView = MainView(app, self)
