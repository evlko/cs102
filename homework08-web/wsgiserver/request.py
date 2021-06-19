import dataclasses
import io
import sys
import typing as tp
from urllib.parse import unquote

from httpserver import HTTPRequest


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


@dataclasses.dataclass
class WSGIRequest(HTTPRequest):  # type:ignore
    def to_environ(self) -> tp.Dict[str, tp.Any]:
        normalized_url = url_normalize(self.url.decode())
        environ = {
            "REQUEST_METHOD": self.method.decode(),
            "SCRIPT_NAME": "",
            "PATH_INFO": self._get_path_info(normalized_url),
            "QUERY_STRING": self._get_query_string(normalized_url),
            "CONTENT_TYPE": self.headers.get(b"Content-Type", b"").decode(),
            "CONTENT_LENGTH": self.headers.get(b"Content-Length", b"").decode(),
            "SERVER_PROTOCOL": b"HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": b"http",
            "wsgi.input": io.BytesIO(self.body),
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": True,
            "wsgi.multiprocess": False,
            "wsgi.run_once": True,
        }

        for header_name in self.headers:
            environ.update(
                {
                    "HTTP_"
                    + (header_name.decode().upper().replace("-", "_")): self.headers[
                        header_name
                    ].decode()
                }
            )

        return environ

    def _get_path_info(self, url: str) -> str:
        return url.split("?", 1)[0]

    def _get_query_string(self, url: str) -> str:
        return url.split("?", 1)[1] if "?" in url else ""
