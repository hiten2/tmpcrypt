import socket

if __name__ == "__main__":
    buflen = 1 << 24
    sock = socket.create_connection(("skraal.asuscomm.com", 80), timeout = 10)

    try:
        with open("documents.zip.encrypted", "wb") as fp:
            read = 0

            while 1:
                chunk = sock.recv(buflen)

                if not chunk:
                    break
                fp.write(chunk)
                read += len(chunk)
                print "Read %u bytes..."
                del chunk
    finally:
        sock.close()
