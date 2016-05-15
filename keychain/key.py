from base64 import b64decode
from hashlib import md5
# rhel, fedora: sudo dnf install m2crypto
# other: pip install M2Crypto
from M2Crypto import EVP


class Key(object):
    def __init__(self, data, iterations=0, validation='', identifier=None,
                 level=None):
        self.MINIMUM_ITERATIONS = 1000
        self.identifier = identifier
        self.level = level
        self.encryptedKey = SaltedString(data)
        self.decryptedKey = None
        self.iterations = max(int(iterations), self.MINIMUM_ITERATIONS)
        self.validation = validation

    def unlock(self, password):
        key, iv = self.derivePBKDF2(password)

        self.decryptedKey = self.decryptAES(
            key=key,
            iv=iv,
            encryptedString=self.encryptedKey.data,
        )

        return self.validateKey()

    def decrypt(self, b64String):
        encrypted = SaltedString(b64String)
        key, iv = self.deriveOpenSSL(self.decryptedKey, encrypted.salt)

        return self.decryptAES(key=key, iv=iv, encryptedString=encrypted.data)

    def decryptAES(self, key, iv, encryptedString):
        aes = EVP.Cipher('aes_128_cbc', key, iv, key_as_bytes=False,
                         padding=False, op=0)

        return self.stripPadding(aes.update(encryptedString) + aes.final())

    def deriveOpenSSL(self, key, salt):
        key = key[0:-16]
        keyAndIV = ''
        curr = ''
        while len(keyAndIV) < 32:
            curr = md5(curr + key + salt).digest()
            keyAndIV += curr

        return keyAndIV[0:16], keyAndIV[16:]


    def derivePBKDF2(self, password):
        keyAndIV = EVP.pbkdf2(
            password,
            self.encryptedKey.salt,
            self.iterations,
            32,
        )
        return keyAndIV[0:16], keyAndIV[16:]

    def stripPadding(self, decrypted):
        padding = ord(decrypted[-1])
        if padding < 16:
            decrypted = decrypted[:-padding]

        return decrypted

    def validateKey(self):
        return self.decrypt(self.validation) == self.decryptedKey


class SaltedString(object):
    def __init__(self, base64String):
        self.SALTED_PREFIX = 'Salted__'
        self.ZERO_INIT_VECTOR = '\x00' * 16
        self.salt = None
        self.data = None

        decodedString = b64decode(base64String)
        if decodedString.startswith(self.SALTED_PREFIX):
            self.salt = decodedString[8:16]
            self.data = decodedString[16:]
        else:
            self.salt = self.ZERO_INIT_VECTOR
            self.data = decodedString
