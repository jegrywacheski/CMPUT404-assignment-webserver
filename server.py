#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()

        if not self.data:
            return

        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        # split string
        parse_request = self.data.decode('utf-8').split("\r\n")
        method, path, http = parse_request[0].split(" ")

        header = ""

        # status code of “405 Method Not Allowed” for any method you cannot handle
        if "GET" not in method:
            header = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            self.request.sendall(header.encode())
            return

        # webserver can serve files from ./www
        wpath = 'www' + path

        if os.path.isdir(wpath):
            # webserver can return index.html from directories (paths that end in /)
            if wpath[-1] == '/':
                wpath = wpath + "index.html"
            else:
                # use 301 to correct paths
                header = "HTTP/1.1 301 Moved Permanently\r\n"
                header = header + f"Location: http://127.0.0.1:8080{path}/\r\n\r\n"
                self.request.sendall(header.encode())
                return

        # security check
        # convert wpath to real path in case it includes /../../
        # check if it still begins in allowable directory www, is a subpath
        given_path = os.path.realpath(wpath)
        start_path = os.path.realpath("www")
        if not given_path.startswith(start_path):
            header = "HTTP/1.1 404 Not Found\r\n\r\n"
            self.request.sendall(header.encode())
            return

        msg = ""
        try:
            # read file and send contents
            f = open(wpath, 'r')
            contents = f.read()
            f.close()
            header = header + "HTTP/1.1 200 OK\r\n"

            mime = ""
            if wpath.endswith("html"):
                # webserver supports mime-types for HTML
                mime = "text/html"
            elif wpath.endswith("css"):
                # webserver supports mime-types for CSS
                mime = "text/css"

            header = header + "Content-Type: " + mime + "\r\n\r\n"
            msg = header + contents


        except Exception as e:
            header = "HTTP/1.1 404 Not Found\r\n\r\n"
            msg = header

        self.request.sendall(msg.encode())
        return


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
