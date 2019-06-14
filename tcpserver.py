import os
import socket
import sys
import traceback

def main():
    buflen = 1 << 24
    print "Opening server on :80..."
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("", 80))
    sock.listen(1)

    while 1:
        try:
            conn, remote = socket.accept()
        except socket.error:
            continue

        try:
            if not raw_input("Received connection from %s:%u, accept? [Y/n]").strip().upper() == "Y":
                print "Tossing."
                conn.close()
                del conn
                del remote
                continue

            with open("f:\\documents.zip.encrypted", "rb") as fp:
                sent = 0
                fp.seek(0, os.SEEK_END)
                size = fp.tell()
                fp.seek(0, so.SEEK_SET)

                print "Sending %u bytes..." % size
                
                while 1:
                    chunk = fp.read(buflen)

                    if not chunk:
                        break
                    conn.sendall(chunk)
                    sent += len(chunk)
                    print "Sent %u/%u bytes (%.2f%%)..." % (sent, size, sent / float(size) * 100)
                    del chunk
                del sent
                del size
                print "Done."
        except KeyboardInterrupt:
            break
        except socket.error:
            conn.close()
            print "Connection closed."

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print >> sys.stderr, traceback.format_exc(e)
    raw_input("Press Enter to exit...")
