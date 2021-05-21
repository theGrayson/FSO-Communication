import secrets as sc
import hashlib

#Public Variables
prime = 23
base = 5  

#Generates the private key for the user
def generateSecKey():
    secKey = sc.choice(range(0,420666)) #secret key
    int(secKey)
    return secKey

__secKey = generateSecKey() #__ makes the variable private
#print(__secKey)

#Generate the exchange key
def generateKey():
    key = (base**__secKey) % prime
    #sendKey = hashlib.sha256(str(key).encode()).hexdigest()
    #str(sendKey)
    #return sendKey
    return key

#print(generateKey())

#Computes the shared key, i is the key that is gained from the exchange
def computeKey(i):
    sharedKey = (int(i) ** __secKey) % prime
    keyGen = hashlib.sha256(str(sharedKey).encode()).hexdigest() #encoded key
    str(keyGen)
    return keyGen
    #return sharedKey


