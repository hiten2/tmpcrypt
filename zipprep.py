import os
import sys
import tkFileDialog
import traceback

__doc__ = "zipprep - recursively prepare pathnames within a directory for use in a ZIP file"

def zip_normalize_path(p):
    """make a path comply with the ZIP character set by removing invalid characters"""
    p = list(p)

    for i, c in enumerate(p):
        try:
            c.encode("ascii")
        except:
            p[i] = ""
    return "".join(p)

if __name__ == "__main__":
    try:
        print "zipprep - make pathnames below a particular directory ZIP-safe"
        root = tkFileDialog.askdirectory(title = "Choose directory")

        if not root:
            print "Invalid directory."
            raw_input("Press Enter to exit...")
            sys.exit(1)
        print """You've selected \"%s\",
however, this will sanitize all pathnames beneath it (inclusive):
are you sure you want to continue? [Y/n]""" % root,
        root_parent = os.path.dirname(root)
        root_name = os.path.basename(root)

        if not raw_input().strip().upper() == "Y":
            raw_input("Press Enter to exit...")
            sys.exit(1)
        dirs = []
        files = []
        
        for r, ds, fs in os.walk(root, topdown = False):
            dirs += [os.path.join(r, d) for d in ds]
            files += [os.path.join(r, f) for f in fs]
    
        for path in files + dirs + [root]:
                i = 1
                norm = os.path.join(os.path.dirname(path), zip_normalize_path(os.path.basename(path)))
    
                if path == norm:
                    continue
    
                while os.path.exists(norm):
                    norm = (".%u" % i).join(os.path.splitext(norm))
                    i += 1
                print "\"%s\" -> \"%s\"" % (path, norm)
                os.rename(path, norm)
        print "Sanitized."
    except Exception as e:
        print >> sys.stderr, traceback.format_exc(e)
        raw_input("Press Enter to exit...")
