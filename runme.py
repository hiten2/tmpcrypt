import os
import sys
import zipfile

sys.path.append(os.path.realpath(__file__))

import tmpcrypt
import zipprep

if __name__ == "__main__":
    print "Running zipprep.py on F:..."
    zipprep.sys.argv.insert(1, "F:")
    zipprep.main()
    zipfile.ZipFile()
    tmpcrypt.sys.argv.insert(1, "F:")
