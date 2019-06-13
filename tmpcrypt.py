import math
import os
import sys
import tkFileDialog
import traceback

__doc__ = "(temporary) rudimentary encryption routine"

class Blocks:
    """unpadded block iterator"""
    
    def __init__(self, size):
        self.size = size

    def __call__(self, s, start = 0):
        i = start

        while i < len(s):
            yield i
            i += self.size

class RBlocks:
    """identical to Blocks, but generates the same blocks in reverse order"""
    
    def __init__(self, size):
        self.size = size

    def __call__(self, s, start = 0):
        i = start + (len(s) - start) - (len(s) - start) % self.size # operate on proper offset

        while i >= 0:
            yield i
            i -= self.size

class TMPCrypt:
    """insecure cipher: for one-time use"""
    
    P_BOX = range(256) # octet range
    
    def __init__(self, key):
        self.key = bytearray(key)
        self.dki = 0 # decryption key index
        self.eki = 0 # encryption key index
        self.p_box = list(TMPCrypt.P_BOX)

        # prep P-Box using Snapper's whirlpool algorithm

        # brief refresher of the whirlpool algorithm:
        #   for each octet as index in key:
        #       P-Box left of index is rotated right
        #       P-Box right of index is rotated left

        for k in self.key:
            # rotate left side right (element at k - 1 is now at 0)

            self.p_box[:k] = self.p_box[k - 1:k] + self.p_box[:k - 1]

            # rotate right side left (element at k + 1 is now at 255)

            self.p_box[k + 1:] = self.p_box[k + 2:] \
                + self.p_box[k + 1:k + 2]
        self.rp_box = sorted(range(256), key = lambda i: self.p_box[i])

    def decrypt(self, s):
        bi = None # override garbage collection
        s = bytearray(s)

        for i, k in enumerate(self.key[self.dki:]):
            # permute

            s[i] = self.rp_box[s[i]]

            # XOR with key

            s[i] ^= k

            self.dki += 1

        self.dki %= len(self.key)

        for b in Blocks(len(self.key))(s, self.dki):
            for k in self.key:
                bi = b + self.dki # block index + decryption key index

                if bi >= len(s):
                    break

                # permute

                s[bi] = self.rp_box[s[bi]]
                
                # XOR with key
                
                s[bi] ^= k

                self.dki += 1
            self.dki %= len(self.key)
        return str(s)
    
    def encrypt(self, s):
        bi = None # override garbage collection
        s = bytearray(s)

        for i, k in enumerate(self.key[self.eki:]):
            # XOR with key

            s[i] ^= k

            # permute

            s[i] = self.rp_box[s[i]]

            self.eki += 1

        self.eki %= len(self.key)

        for b in Blocks(len(self.key))(s, self.eki):
            for k in self.key:
                bi = b + self.eki # block index + encryption key index

                if bi >= len(s):
                    break
                # XOR with key
                
                s[bi] ^= k

                # permute

                s[bi] = self.p_box[s[bi]]

                self.eki += 1
            self.eki %= len(self.key)
        return str(s)

if __name__ == "__main__":
    buflen = 1 << 24 # 16 MiB
    ctext = None
    path = tkFileDialog.askopenfilename(title = "Source (file)")

    if not path:
        print "Invalid path."
        raw_input("Press Enter to exit...")
        sys.exit(1)
    dest = tkFileDialog.asksaveasfilename(title = "Destination (file)")
    
    if not dest:
        print "Invalid path."
        raw_input("Press Enter to exit...")
        sys.exit(1)
    tmpcrypt = TMPCrypt(raw_input("Key: "))
    func = tmpcrypt.encrypt

    if "-d" in sys.argv[1:] or "--decrypt" in sys.argv[1:]:
        func = tmpcrypt.decrypt
    
    try:
        with open(path, "rb") as sfp:
            with open(dest, "r+b" if os.path.exists(dest) else "wb") as dfp:
                while 1:
                    chunk = sfp.read(buflen)

                    if not chunk:
                        break
                    dfp.write(func(chunk))
                    del chunk
                dfp.truncate()
    
                try:
                    os.fdatasync(dfp.fileno())
                except:
                    print "os.fdatasync failed.  Continuing anyway."
                print "Encrypted to \"%s\"" % dest
    except Exception as e:
        print >>sys.stderr, traceback.format_exc(e)
    raw_input("Press Enter to exit...")
    sys.exit()
