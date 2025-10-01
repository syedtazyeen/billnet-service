#!/usr/bin/env python
# pylint: disable-all
import uvicorn
from decouple import config


def main():
    """Main function to start the server."""
    host = config("HOST", default="127.0.0.1")
    port = config("PORT", default=8000, cast=int)
    reload = config("DEBUG", default=False, cast=bool)
    log_level = config("LOG_LEVEL", default="info", cast=str).lower()

    uvicorn.run("config.asgi:application", host=host, port=port, reload=reload, log_level=log_level)


if __name__ == "__main__":
    main()
