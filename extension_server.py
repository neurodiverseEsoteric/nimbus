#!/usr/bin/env python3

# extension_server.py
# This simple script launches a webserver, which hosts the browser's extension
# files so they can be loaded into the DOM without suffering from issues
# regarding origin policies.

# Import whatever we need to run.
import os
from http.server import SimpleHTTPRequestHandler
import http.server
try: from PyQt4.QtCore import QThread
except: from PySide.QtCore import QThread
import common

class ExtensionServerThread(QThread):
    def run(self):
        os.chdir(common.extensions_folder)
        HandlerClass = SimpleHTTPRequestHandler
        ServerClass  = http.server.HTTPServer
        Protocol     = "HTTP/1.0"

        port = 8133
        server_address = ('127.0.0.1', port)

        HandlerClass.protocol_version = Protocol
        self.httpd = ServerClass(server_address, HandlerClass)

        sa = self.httpd.socket.getsockname()
        self.httpd.serve_forever()
