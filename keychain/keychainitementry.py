import logging
from utils import enum

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
                 designation=Designation.OTHER):
        self.key = key
        self.value = value
        self.designation = designation
        self.isUsername = designation == Designation.USER
        self.isPassword = designation == Designation.PW
        self.isSection = designation == Designation.SECTION
        self.isSecret = isSecret or self.isPassword \
                                 or 'password' in key.lower()
        self.isVisible = isVisible

    def getKey(self):
        if self.isPassword:
            key = 'Password'
        elif self.isUsername:
            key = 'Username'
        else:
            key = self.key
        return key.capitalize()

    def getValue(self):
        value = unicode(self.value)
        if self.isSecret:
            value = '***'
        elif len(value) > 40:
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
