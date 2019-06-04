import math
import os
import sys

__doc__ = "(temporary) rudimentary encryption routine"

class Blocks:
    """unpadded block iterator"""
    
    def __init__(self, size):
        self.size = size

    def __call__(self, s):
        i = 0

        while i < len(s):
            yield i
            i += self.size

class RBlocks:
    """identical to Blocks, but generates the same blocks in reverse order"""
    
    def __init__(self, size):
        self.size = size

    def __call__(self, s):
        i = len(s) - len(s) % self.size # operate on proper offset

        while i >= 0:
            yield i
            i -= self.size

class TMPCrypt:
    """insecure cipher: for one-time use"""
    
    P_BOX = range(256) # octet range
    
    def __init__(self, key):
        self.key = bytearray(key)
        self.p_box = list(TMPCrypt.P_BOX)

        # prep P-Box using Snapper's whirlpool algorithm

        # brief refresher of the whirlpool algorithm:
        #   for each octet as index in key:
        #       P-Box left of index is rotated right
        #       P-Box right of index is rotated right

        for k in self.key:
            # rotate left side right (element at k - 1 is now at 0)

            self.p_box[:k] = self.p_box[k - 1:k] + self.p_box[:k - 1]

            # rotate right side left (element at 255 is now at k + 1)

            self.p_box[k + 1:] = self.p_box[-1:] + self.p_box[k + 1:-1]
        self.rp_box = sorted(range(256), key = lambda i: self.p_box[i])
        print [self.p_box]
        print [self.rp_box]

    def decrypt(self, s):
        bi = None # override garbage collection
        s = bytearray(s)

        for b in Blocks(len(self.key))(s):
            for i, k in enumerate(self.key):
                bi = b + i # block index + internal index

                if bi >= len(s):
                    break

                # permute

                s[bi] = self.rp_box[s[bi]]
                
                # XOR with key
                
                s[bi] ^= k
        return str(s)
    
    def encrypt(self, s):
        bi = None # override garbage collection
        s = bytearray(s)

        for b in Blocks(len(self.key))(s):
            for i, k in enumerate(self.key):
                bi = b + i # block index + internal index

                if bi >= len(s):
                    break
                # XOR with key
                
                s[bi] ^= k

                # permute

                s[bi] = self.p_box[s[bi]]
        return str(s)

if __name__ == "__main__":
    k = ""#some key"
    s = "this is a test"
    t = TMPCrypt(k)
    c = t.encrypt(s)
    p = t.decrypt(c)
    print s.encode("hex")
    print c.encode("hex")
    print p.encode("hex")
    print s == p
    sys.exit()
    path = None

    while 1:
        path = raw_input("Path: ")
        
        if os.path.exists(path):
            break
        print "That path doesn't exist."
    dest = path + ".encrypted"

    if os.path.exists(dest):
        if not raw_input("Destination exists: overwrite? [Y/n]") \
               .strip().upper() == "Y":
            sys.exit(1)
    ctext = None
    tmpcrypt = TMPCrypt(raw_input("Key: "))

    with open(path, "rb") as sfp:
        with open(path, "r+b" if os.path.exists(dest) else "wb") as dfp:
            dfp.write(tmpcrypt(sfp.read()))
            dfp.truncate()

            try:
                os.fdatasync(dfp.fileno())
            except:
                print "os.fdatasync failed.  Continuing anyway."
    print "Encrypted to \"%s\"" % dest
