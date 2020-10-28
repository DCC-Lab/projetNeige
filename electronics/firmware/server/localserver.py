# import http.server
# import socketserver
#
#
# PORT = 80
# # Handler = http.server.SimpleHTTPRequestHandler
# Handler = http.server.CGIHTTPRequestHandler
#
# with socketserver.TCPServer(("192.168.2.30", PORT), Handler) as httpd:
#     print("serving at port", PORT)
#     httpd.serve_forever()

#
# #!/usr/bin/env python
# """
# Very simple HTTP server in python (Updated for Python 3.7)
# Usage:
#     ./dummy-web-server.py -h
#     ./dummy-web-server.py -l localhost -p 8000
# Send a GET request:
#     curl http://localhost:8000
# Send a HEAD request:
#     curl -I http://localhost:8000
# Send a POST request:
#     curl -d "foo=bar&bin=baz" http://localhost:8000
# """
#
#
# import argparse
# from http.server import HTTPServer, BaseHTTPRequestHandler
#
#
# class Server(BaseHTTPRequestHandler):
#     def _set_headers(self):
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#
#     def _html(self, message):
#         """This just generates an HTML document that includes `message`
#         in the body. Override, or re-write this do do more interesting stuff.
#         """
#         content = f"<html><body><h1>Hello. This is a test server</h1></body></html>"
#         return content.encode("utf8")  # NOTE: must return a bytes object!
#
#     def do_GET(self):
#         self._set_headers()
#         self.wfile.write(self._html("hi!"))
#
#     def do_HEAD(self):
#         self._set_headers()
#
#     def do_POST(self):
#         # Doesn't do anything with posted data
#         self._set_headers()
#         self.wfile.write(self._html("POST!"))
#
#
# def run(server_class=HTTPServer, handler_class=Server, addr="localhost", port=8000):
#     server_address = (addr, port)
#     httpd = server_class(server_address, handler_class)
#
#     print(f"Starting httpd server on {addr}:{port}")
#     httpd.serve_forever()
#
#
# if __name__ == "__main__":
#
#     parser = argparse.ArgumentParser(description="Run a simple HTTP server")
#     parser.add_argument(
#         "-l",
#         "--listen",
#         default="192.168.2.30",
#         help="Specify the IP address on which the server listens",
#     )
#     parser.add_argument(
#         "-p",
#         "--port",
#         type=int,
#         default=80,
#         help="Specify the port on which the server listens",
#     )
#     args = parser.parse_args()
#     run(addr=args.listen, port=args.port)

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers),
                     post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=S, port=80):
    logging.basicConfig(level=logging.INFO)
    server_address = ('192.168.2.30', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    print(httpd)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
