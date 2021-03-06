import json
import logging
import os
import sys

from key import Key
from keychainitem import KeychainItem

logger = logging.getLogger('PassPy.Keychain')

class Keychain(object):
    def __init__(self, path, vault, entryConfig):
        self.KEYS_FILE = 'encryptionKeys.js'
        self.CONTENTS_FILE = "contents.js"
        self.vault = os.path.join(os.path.expanduser(path), 'data', vault)
        self.keys = {}
        self.itemIndexName = {}
        self.itemIndexType = {}
        self.locked = True
        self.entryConfig = entryConfig

    def unlock(self, password):
        self.loadKeys()
        unlocked = map(lambda key: key.unlock(password), self.keys.values())
        self.locked = not reduce(lambda x, y: x and y, unlocked)
        if not self.locked:
            self.loadItems()

        return not self.locked

    def lock(self):
        self.keys = {}
        self.itemIndexName = {}
        self.itemIndexType = {}
        self.locked = True

    def loadKeys(self):
        path = os.path.join(self.vault, self.KEYS_FILE)
        try:
            with open(path, 'r') as KEYS_FILE:
                keyFileData = json.load(KEYS_FILE)
        except IOError, e:
            logger.error('Could not read {}: {}'.format(path, e))
            sys.exit(1)
        except Exception, e:
            logger.error('Error while reading {}: {}'.format(path, e))
            sys.exit(1)

        for entry in keyFileData['list']:
            key = Key(**entry)
            self.keys[key.identifier] = key

    def loadItems(self):
        path = os.path.join(self.vault, self.CONTENTS_FILE)
        try:
            with open(path, 'r') as CONTENTS_FILE:
                items = json.load(CONTENTS_FILE)
        except IOError, e:
            logger.error('Could not read {}: {}'.format(path, e))
            sys.exit(1)
        except Exception, e:
            logger.error('Error while reading {}: {}'.format(path, e))
            sys.exit(1)

        for itemInfo in items:
            identifier = itemInfo[0]
            type = itemInfo[1]
            name = unicode(itemInfo[2])
            if not type.startswith('system'):
                item = KeychainItem(self, identifier, type, name, self.entryConfig)
                logger.debug(item)
                self.itemIndexName[name] = item
                if item.type in self.itemIndexType:
                    self.itemIndexType[item.type][item.name] = item
                else:
                    self.itemIndexType[item.type] = {item.name: item}

    def getKey(self, identifier=None, securityLevel=None):
        key = None
        if identifier and identifier in self.keys:
            key = self.keys[identifier]
        elif securityLevel:
            for currKey in self.keys.values():
                if currKey.level == securityLevel:
                    key = currKey

        return key

    def getItems(self, name=None, type=None):
        items = self.itemIndexName
        if type:
            items = self.itemIndexType[type]
        if name:
            name = name.lower()
            items = {k: v for k, v in items.items() if name in k.lower()}

        return items

    def getCategories(self):
        return self.itemIndexType.keys()
