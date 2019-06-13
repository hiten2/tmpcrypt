import os
import sys

sys.path.append(os.path.realpath(__file__))

from baseserver import BaseHTTPServer, TCPConfig

if __name__ == "__main__":
    class MainConfig(TCPConfig):
        ADDRESS = ("", 80)
    
    server = BaseHTTPServer(sock_config = MainConfig)
    server.resolve = lambda r: "f:\\documents.zip.encrypted" # force all traffic to this path
    print "Forcing all paths to f:\\documents.zip.encrypted"
    server()
