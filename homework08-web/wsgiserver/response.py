import dataclasses
import typing as tp

from httpserver import HTTPResponse


@dataclasses.dataclass
class WSGIResponse(HTTPResponse):  # type:ignore
    status: int = 200

    def start_response(
        self,
        status: str,
        response_headers: tp.List[tp.Tuple[str, str]],
        exc_info: tp.Optional[tp.Any] = None,
    ) -> None:
        self.status = int(status.split(" ", 1)[0])
        for header in response_headers:
            self.headers.update({header[0]: header[1]})
