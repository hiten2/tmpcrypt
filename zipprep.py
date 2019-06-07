import os
import tkFileDialog

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
    root = tkFileDialog.askdirectory(title = "Choose directory")

    if not root:
        print "Invalid directory."
        raw_input("Press Enter to exit...")
    print "You've selected \"%s\"," % root
    root_parent = os.path.dirname(root)
    root_name = os.path.basename(root)

    if not raw_input("""however, this will sanitize all pathnames below the directory:
are you sure you want to continue? [Y/n] """).strip().upper() == "Y":
        raw_input("Press Enter to exit...")
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
    raw_input("Press Enter to exit...")