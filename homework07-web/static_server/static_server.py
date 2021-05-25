import datetime
import mimetypes
import pathlib
import time
import typing as tp
from socketserver import BaseRequestHandler
from urllib.parse import unquote, urlparse

from httpserver import BaseHTTPRequestHandler, HTTPRequest, HTTPResponse, HTTPServer


def path_resolver(path: str) -> str:
    curr_path: tp.List[str] = []
    for curr_elem in path.rsplit("?", 1)[0].split("/"):
        if curr_elem == "..":
            try:
                curr_path.pop()
            except IndexError:
                pass
        elif curr_elem == ".":
            continue
        else:
            curr_path.append(curr_elem)
    try:
        if "." in curr_path[-2] and curr_path[-1] == "":
            del curr_path[-1]
    except IndexError:
        pass
    return "/".join(curr_path)


def url_normalize(path: str) -> str:
    normalized_path = path_resolver(path.replace("//", "/"))
    if normalized_path[0] == "/":
        normalized_path = normalized_path[1:]
    return unquote(normalized_path) + (
        "index.html" if len(normalized_path) == 0 or normalized_path[-1] == "/" else ""
    )


class StaticHTTPRequestHandler(BaseHTTPRequestHandler):  # type:ignore
    def __init__(self, *args, **kwargs) -> None:  # type:ignore
        super().__init__(*args, **kwargs)
        self.document_root: pathlib.Path = self.server.document_root  # type: ignore

    def handle_request(self, request: HTTPRequest) -> HTTPResponse:
        # NOTE: https://tools.ietf.org/html/rfc3986
        # NOTE: echo -n "GET / HTTP/1.0\r\n\r\n" | nc localhost 5000
        headers = {
            "Server": "Lav's Server",
            "Date": datetime.datetime.now().strftime("%a, %d %b %Y %H:%m:%S"),
            "Allow": "GET, HEAD",
        }

        if request.method not in (b"GET", b"HEAD"):
            return HTTPResponse(405, headers, b"")

        normalized_path = url_normalize(request.url.decode())

        mime = mimetypes.guess_type(normalized_path)[0]
        if mime is None:
            headers["Content-Type"] = ""
        else:
            headers["Content-Type"] = mime

        file_path = self.document_root / normalized_path

        if request.method == b"HEAD":
            if file_path.exists():
                return HTTPResponse(200, headers, b"")
            else:
                return HTTPResponse(404, headers, b"")

        if file_path.exists():
            with file_path.open("rb") as f:
                data = f.read()
                headers["Content-Length"] = str(len(data))

                return HTTPResponse(200, headers, data)

        else:
            return HTTPResponse(404, headers, b"")


class StaticServer(HTTPServer):  # type:ignore
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        document_root: pathlib.Path = pathlib.Path("/tmp"),
        backlog_size: int = 1,
        max_workers: int = 1,
        timeout: tp.Optional[float] = None,
        request_handler_cls: tp.Type[BaseRequestHandler] = StaticHTTPRequestHandler,  # type:ignore
    ):
        super().__init__(
            host, port, backlog_size, max_workers, timeout, request_handler_cls  # type:ignore
        )
        self.document_root = document_root


if __name__ == "__main__":
    document_root = pathlib.Path("static") / "root"
    server = StaticServer(
        port=5000,
        max_workers=5,
        timeout=2,
        document_root=document_root,
        request_handler_cls=StaticHTTPRequestHandler,  # type:ignore
    )
    server.serve_forever()
