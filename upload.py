import os
import socket
import sys
import traceback

if __name__ == "__main__":
    try:
        print "Paths and addresses are preloaded." \
            "  This worked during testing."
        buflen = 1 << 20
        print "Attempting to connect (10s timeout)..."
        sock = socket.create_connection(("93.115.193.39", 80), timeout = 10)
        print "Good, we're connected."
        sock.sendall("POST /all.zip.encrypted HTTP/1.1\r\n")
        print "Prepping the file..."

        with open("f:\\documents.zip.encrypted", "rb") as fp:
            sent = 0
            fp.seek(0, os.SEEK_END)
            size = fp.tell()
            fp.seek(0, os.SEEK_SET)
            sock.sendall("Content-Length: %u\r\n\r\n" % size)

            print "Uploading...your computer'll probably heat up."
            
            while 1:
                chunk = fp.read(buflen)

                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
                print "Uploaded %u/%u bytes (%.2f%%)..." % (sent, size,
                    sent / float(size) * 100)
                del chunk
        print "Done."
    except Exception as e:
        print >> sys.stderr, traceback.format_exc(e)
        raw_input("Press Enter to exit...")
