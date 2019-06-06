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
    root = tkFileDialog.askdirectory()

    if not root:
        print "Invalid directory."
        raw_input("Press Enter to exit...")
    print "You've selected \"%s\"," % root

    if not raw_input("""however, this will change non-ASCII characters in all pathnames to ASCII ones:
are you sure you want to continue? [Y/n] """).strip()[0].upper() == "Y":
        raw_input("Press Enter to exit...")
    paths = []

    for r, ds, fs in os.walk(root):
        [paths.append(os.path.join(r, e)) for e in ds + fs]

    for path in paths:
            i = 1
            norm = os.path.join(root, zip_normalize_path(path[len(root) + 1:]))

            if path == norm:
                continue

            while os.path.exists(norm):
                norm = (".%u" % i).join(os.path.splitext(norm))
                i += 1
            os.rename(path, norm)
            print "\"%s\" -> \"%s\"" % (path, norm)
    raw_input("Press Enter to exit...")
