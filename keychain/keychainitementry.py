import logging
from utils import enum, translate

Designation = enum(
    USER='username',
    PW='password',
    URL='url',
    SECTION='section',
    OTHER='other',
)

logger = logging.getLogger('PassPy.KeychainItemEntry')


class KeychainItemEntry(object):
    def __init__(self, key, value, isSecret=False, isVisible=True,
                 designation=Designation.OTHER, translate=None):
        self.key = key
        self.value = value
        self.designation = designation
        self.isUsername = designation == Designation.USER
        self.isPassword = designation == Designation.PW
        self.isSection = designation == Designation.SECTION
        self.isUrl = designation == Designation.URL
        self.isSecret = isSecret or self.isPassword \
                                 or 'password' in key.lower() \
                                 or ('pin' in key.lower() and value.isdigit()) \
                                 or key == 'cvv'
        self.isVisible = isVisible
        self.translate = translate

    def getKey(self):
        key = self.key
        if self.isPassword:
            key = 'Password'
        elif self.isUsername:
            key = 'Username'
        elif self.translate:
            key = translate(self.key, self.translate)

        return key.title()

    def getValue(self, trimmed=True):
        value = unicode(self.value)
        if self.isSecret:
            value = '******'
        elif trimmed and len(value) > 40:
            value = '{}...'.format(value[:40])

        return value

    def __str__(self):
        return u'SECRET: {} VISIBLE: {} DESIGNATION: {} K: {} V: {}'.format(
            str(self.isSecret).ljust(5),
            str(self.isVisible).ljust(5),
            self.designation.ljust(9),
            self.key.ljust(30),
            self.getValue()
        )
