import argparse
import logging
import os
import socket
from multiprocessing import Process

from constants import *
from socket_methods import SocketRequestHandler, SocketResponseHandler


class Server:
    def __init__(self, root, port):
        self._document_root = root
        self.is_root_document_exist()
        self.sock = socket.socket()
        self.sock.bind((HOST, port))
        self.sock.listen()

    def is_root_document_exist(self):
        if not os.path.isdir(self._document_root):
            raise Exception('Нет корневого документа')

    def create_request(self, client_socket):
        request_bytes = b''
        expected_size = 0
        while len(request_bytes) >= expected_size:
            chunk_bytes = client_socket.recv(CHUNK_SIZE)
            request_bytes += chunk_bytes
            if SocketRequestHandler.is_length_exceeded(request_bytes) or \
                    SocketRequestHandler.is_complete(request_bytes):
                break
            expected_size += CHUNK_SIZE
        return SocketRequestHandler(request_bytes)

    def serve_forever(self):
        while True:
            client_socket, address_info = self.sock.accept()
            client_socket.settimeout(CLIENT_TIMEOUT)
            with client_socket:
                request = self.create_request(client_socket)
                response = SocketResponseHandler(request, self._document_root)
                client_socket.sendall(response.to_bytes())


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--workers', help='Count of workers', default=1, type=int)
    parser.add_argument('-r', '--document_root', help='Document root path', default='.', type=str)
    parser.add_argument('-p', '--port', help='Port', default=PORT, type=int)
    args = parser.parse_args()

    workers_count = args.workers if args.workers > 0 else 1
    try:
        server = Server(args.document_root, args.port)
    except Exception as e:
        logging.error(e)
        exit()
    workers = []

    for _ in range(workers_count):
        worker = Process(target=server.serve_forever)
        worker.start()
        workers.append(worker)
    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        for worker in workers:
            worker.terminate()
            logging.info(f'Worker {worker.pid} was terminated')
