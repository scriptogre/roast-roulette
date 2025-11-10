from datetime import datetime

from debug_toolbar.middleware import DebugToolbarMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app import enums
from app.fasthtml import FastHTML
from app.lifespan import lifespan
from main.config import settings


# 1. Create application
app = FastHTML(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# 2. Add middlewares
app.add_middleware(
    DebugToolbarMiddleware,
    panels=["debug_toolbar.panels.tortoise.TortoisePanel"],
)

app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=["192.168.0.0/16", "172.16.0.0/12", "10.0.0.0/8"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS.split(","),
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)


# 3. Mount static & media directories
app.mount(
    "/static",
    StaticFiles(directory=settings.STATIC_DIR),
    name="static",
)
app.mount(
    "/media",
    StaticFiles(directory=settings.MEDIA_DIR),
    name="media",
)

# 4. Add templates
app.add_templates(
    directory=settings.TEMPLATES_DIR,
    globals={
        "GameStatus": enums.GameStatus,
        "now": datetime.now,
    },
)

# 5. Include routers
app.include_router(routes.router)
