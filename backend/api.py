from main import app as _app
from starlette.types import ASGIApp, Receive, Scope, Send

class StripPrefixMiddleware:
    def __init__(self, app: ASGIApp, prefix: str) -> None:
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"].startswith(self.prefix):
            scope = dict(scope)
            scope["path"] = scope["path"][len(self.prefix):] or "/"
        await self.app(scope, receive, send)

application = StripPrefixMiddleware(_app, "/ai")
handler = application
