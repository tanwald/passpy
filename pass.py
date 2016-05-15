#!/usr/bin/env python

import gi
import logging
import sys

from ConfigParser import ConfigParser

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib
from library.keychain import Keychain
from gui.window import Window
from os import path

################################################################################
# GLOBAL LOGGER
################################################################################

logger = logging.getLogger('PassPy')
logger.setLevel(logging.INFO)

logFormat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
logfilePath = path.join(path.dirname(path.abspath(__file__)), 'pass.log')

logfile = logging.FileHandler(logfilePath)
logfile.setLevel(logging.INFO)
logfile.setFormatter(logging.Formatter(logFormat))

console = logging.StreamHandler()
console.setFormatter(logging.Formatter(logFormat))

logger.addHandler(logfile)
logger.addHandler(console)


################################################################################
# PASSPY GTK APPLICATION
################################################################################

class PassPy(Gtk.Application):
    def __init__(self, config):
        Gtk.Application.__init__(
            self,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        )

        self.config = config
        self.APPLICATION_NAME = 'passpy'
        self.KEYCHAIN_PATH = config.get('keychain', 'path')
        self.VAULT = config.get('keychain', 'vault')
        self.LISTED = config.get('entries', 'listed').split(';')
        self.EXCLUDED = config.get('entries', 'excluded').split(';')
        self.WIN_WIDTH = int(config.get('defaults', 'window.width'))
        self.WIN_HEIGHT = int(config.get('defaults', 'window.height'))

        self.add_main_option(
            'debug',
            ord('d'),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            'Launch in debug mode',
            None
        )

        self.keychain = Keychain(
            self.KEYCHAIN_PATH,
            self.VAULT,
            {'listed': self.LISTED, 'excluded': self.EXCLUDED}
        )

        self.bundle = {k: v for k, v in config.items('bundle')}
        self.locked = True

    def do_activate(self):
        self.window = Window(self)
        self.window.show_all()

    def do_command_line(self, argv):
        options = argv.get_options_dict()

        if options.contains('debug'):
            logger.setLevel(logging.DEBUG)
            logger.info('Launched in debug mode')

        self.activate()

        return 0

    def unlock(self, password):
        if self.keychain.unlock(password):
            self.locked = False

        return not self.locked

    def getItems(self, type=None, name=None):
        return self.keychain.getItems(type=type, name=name)

    def getCategories(self):
        return self.keychain.getCategories()


################################################################################
# MAIN
################################################################################

if __name__ == '__main__':
    config = ConfigParser()
    config.optionxform = str
    config.read(path.join(path.dirname(path.abspath(__file__)), 'pass.cfg'))

    app = PassPy(config)
    logger.info('Started')
    exitcode = app.run(sys.argv)
    logger.info('Finished with exit code {}'.format(exitcode))
    sys.exit(exitcode)
