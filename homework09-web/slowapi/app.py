import http
import typing as tp
from urllib.parse import parse_qsl

from slowapi.request import Request
from slowapi.response import Response
from slowapi.router import Route


class SlowAPI:
    def __init__(self):
        self.routes: tp.List[Route] = []
        self.middlewares = []

    def __call__(self, environ, start_response):
        route = [
            route
            for route in self.routes
            if route.method == environ["REQUEST_METHOD"]
            and (
                route.path == environ["PATH_INFO"]
                or environ["PATH_INFO"].rsplit("/", 1)[0]
                == route.path.rsplit("/", 1)[0]
            )
        ][0]
        
        empty_args = []
        args = (
            environ["PATH_INFO"][route.path.find("{") :].split("&")
            if "{" in route.path
            else empty_args
        )
        args = args if len(args) > 1 and args[0] != "" else empty_args

        query = dict(parse_qsl(environ["QUERY_STRING"]))

        request = Request(
            environ["PATH_INFO"],
            environ["REQUEST_METHOD"],
            query,
            environ["wsgi.input"],
            environ,
        )

        response = route.func(request, *args)
        start_response(
            f"{response.status} {http.client.responses[response.status]}",
            response.headers,
        )

        return [str(response).encode()]

    def route(self, path=None, method=None, **options):
        def wrapper(func):
            self.routes.append(Route(path, method, func))
            return func

        return wrapper

    def get(self, path=None, **options):
        return self.route(path, method="GET", **options)

    def post(self, path=None, **options):
        return self.route(path, method="POST", **options)

    def patch(self, path=None, **options):
        return self.route(path, method="PATCH", **options)

    def put(self, path=None, **options):
        return self.route(path, method="PUT", **options)

    def delete(self, path=None, **options):
        return self.route(path, method="DELETE", **options)

    def add_middleware(self, middleware) -> None:
        self.middlewares.append(middleware)