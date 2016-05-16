import json
import logging
import os

from keychainitementry import KeychainItemEntry, Designation

logger = logging.getLogger('PassPy.KeychainItem')

class KeychainItem(object):
    def __init__(self, keychain, identifier, type, name, entryConfig):
        self.keychain = keychain
        self.vault = keychain.vault
        self.identifier = identifier
        self.type = type
        self.name = name
        self.listed = entryConfig['listed']
        self.excluded = entryConfig['excluded']
        self.translate = entryConfig['translate']

        self.keyId = None
        self.securityLevel = None
        self.encryptedData = None
        self.decryptedData = None
        self.entries = []

    def decrypt(self):
        if not self.decryptedData:
            if not self.encryptedData:
                self.loadItemData()

            key = self.keychain.getKey(
                identifier=self.keyId,
                securityLevel=self.securityLevel,
            )

            decrypted = key.decrypt(self.encryptedData)
            try:
                self.decryptedData = json.loads(decrypted)
            except ValueError:
                self.decryptedData = json.loads(decrypted[:-16])

    def loadItemData(self):
        filename = '{}.1password'.format(self.identifier)
        path = os.path.join(self.vault, filename)

        with open(path, 'rb') as ITEM_FILE:
            itemData = json.load(ITEM_FILE)

        self.keyId = itemData.get('keyID')
        self.securityLevel = itemData.get('securityLevel')
        self.encryptedData = itemData.get('encrypted')

    def getEntries(self):
        if not self.entries:
            self._getEntries(self.decryptedData)

        return self.entries

    def _getEntries(self, root, lastKey=None):
        for key, value in root.items():
            if isinstance(value, list):
                if 'history' not in key.lower():
                    for entry in value:
                        self._buildListEntries(key, entry)
                        self._getEntries(entry, lastKey=key)
            elif lastKey not in self.listed \
                    and key not in self.excluded:
                self.entries.append(
                    KeychainItemEntry(
                        key,
                        value,
                        translate=self.translate
                    )
                )
            else:
                self.entries.append(
                    KeychainItemEntry(
                        key,
                        value,
                        isVisible=False,
                        translate=self.translate
                    )
                )

    def _buildListEntries(self, key, data):
        if key == 'sections':
            self.entries.append(
                self._buildSectionEntry(data)
            )
        elif key == 'fields':
            entry = self._buildFieldEntry(data)
            if entry:
                self.entries.append(entry)
        elif key == 'URLs':
            self.entries.append(
                KeychainItemEntry(
                    'Url',
                    data['url'],
                    designation=Designation.URL
                )
            )

    def _buildSectionEntry(self, data):
        return KeychainItemEntry(
            data['title'],
            ' ',
            designation=Designation.SECTION,
            translate=self.translate
        )

    def _buildFieldEntry(self, data):
        entry = None
        if 'designation' in data \
                and 'name' in data \
                and 'value' in data:
            entry = KeychainItemEntry(
                data['name'],
                data['value'],
                designation=data['designation'],
                translate=self.translate
            )
        elif 't' in data and 'v' in data:
            entry = KeychainItemEntry(
                data['t'],
                data['v'],
                isSecret='k' in data \
                         and data['k'] == 'concealed',
                translate=self.translate
            )

        return entry

    def __str__(self):
        self.decrypt()
        entries = u''
        for entry in self.getEntries():
            if entry.isVisible:
                entries = u'{}\n{}'.format(entries, entry)

        return u'\nNAME {}\nTYPE {}\nENTRIES\n\n{}\n\nJSON\n\n{}\n'.format(
            self.name.upper(),
            self.type,
            entries,
            json.dumps(self.decryptedData, indent=4)
        )
