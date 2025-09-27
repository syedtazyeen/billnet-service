#!/usr/bin/env python
# pylint: disable-all
import uvicorn
from decouple import config


def main():
    """Main function to start the server."""
    # Configuration from environment variables
    host = config("HOST", default="127.0.0.1")
    port = config("PORT", default=8000, cast=int)
    reload = config("DEBUG", default=True, cast=bool)

    uvicorn.run(
        "config.asgi:application", host=host, port=port, reload=reload, log_level="info"
    )


if __name__ == "__main__":
    main()
