#Taken from my repo hopefully secure P2P and adapted

def encryptionToggleMessage(messageBytes, thePrivateKey):
    thePrivateKeyBinaryBits = f"{thePrivateKey:0256b}"
    messageBits = "".join(f"{char:08b}" for char in messageBytes)

    messageBitsLength = len(messageBits)
    keyLen = len(thePrivateKeyBinaryBits)

    if messageBitsLength > keyLen:
        #keyMain = thePrivateKeyBinaryBits.join(thePrivateKeyBinaryBits[0:messageBitsLength-keyLen]) wont work if multiple repeats
        repeats = messageBitsLength // keyLen
        remainder = messageBitsLength % keyLen
        keyMain = (thePrivateKeyBinaryBits * repeats) + thePrivateKeyBinaryBits[0:remainder]
    elif messageBitsLength == keyLen:
        keyMain = thePrivateKeyBinaryBits
    elif messageBitsLength < keyLen:
        keyMain = thePrivateKeyBinaryBits[0:messageBitsLength]
    
    encryptedMessage = ""
    for i in range(messageBitsLength):
        if messageBits[i] == keyMain[i]:
            encryptedMessage += "0"
        else:
            encryptedMessage += "1"
    encryptedBytes = int(encryptedMessage, 2).to_bytes((len(encryptedMessage) + 7) // 8, byteorder="big")
    return encryptedBytes

#test
def test():
#    from keymaker import generatePrivateKey, generatePublicKey
    import secrets
    message = "hello"
    messageBytes = message.encode("utf-8")
    mySecretNumber = secrets.randbits(256)
#    key = generatePrivateKey(mySecretNumber, generatePublicKey(mySecretNumber))
    print("the OG message is: " + str(message))
#    print("the encoded message is: " + str(encryptionToggleMessage(messageBytes, key)))
#    print("running this through the same function returns: " + str(encryptionToggleMessage(encryptionToggleMessage(messageBytes, key), key).decode("utf-8")))