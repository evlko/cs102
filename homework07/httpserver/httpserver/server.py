import datetime
import socket
import threading
import traceback
import typing as tp

from .handlers import BaseHTTPRequestHandler, BaseRequestHandler


class TCPServer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        backlog_size: int = 1,
        max_workers: int = 1,
        timeout: tp.Optional[float] = None,
        request_handler_cls: tp.Type[BaseRequestHandler] = BaseRequestHandler,
    ) -> None:
        self.host = host
        self.port = port
        self.server_address = (host, port)
        # @see: https://stackoverflow.com/questions/36594400/what-is-backlog-in-tcp-connections
        self.backlog_size = backlog_size
        self.request_handler_cls = request_handler_cls
        self.max_workers = max_workers
        self.timeout = timeout
        self._threads: tp.List[threading.Thread] = []
        self._ended = False

    def serve_forever(self) -> None:
        # @see: http://veithen.io/2014/01/01/how-tcp-backlog-works-in-linux.html
        # @see: https://en.wikipedia.org/wiki/Thundering_herd_problem
        # @see: https://stackoverflow.com/questions/17630416/calling-accept-from-multiple-threads
        server_socket = socket.socket()
        server_socket.bind(self.server_address)
        server_socket.listen(self.backlog_size)

        try:
            for i in range(self.max_workers):
                self._threads.append(
                    threading.Thread(target=self.handle_accept, args=(server_socket,))
                )
                self._threads[-1].start()
            for thread in self._threads:
                thread.join()
        except KeyboardInterrupt:
            print("Exiting")
            self._ended = True

        server_socket.close()

    def handle_accept(self, server_socket: socket.socket) -> None:
        while not self._ended:
            try:
                conn, addr = server_socket.accept()
                conn.settimeout(self.timeout)
                handler = self.request_handler_cls(conn, addr, self)
                handler.handle()
            except Exception:
                print(datetime.datetime.now())
                traceback.print_exc()
                print()


class HTTPServer(TCPServer):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        backlog_size: int = 1,
        max_workers: int = 1,
        timeout: tp.Optional[float] = None,
        request_handler_cls: tp.Type[BaseRequestHandler] = BaseHTTPRequestHandler,
    ):
        super().__init__(host, port, backlog_size, max_workers, timeout, request_handler_cls)
