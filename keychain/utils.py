def enum(**enums):
    return type('Enum', (), enums)

def translate(string, dictionary):
    for fromStr, toStr in dictionary.items():
        string = string.replace(fromStr, toStr)
    return string
