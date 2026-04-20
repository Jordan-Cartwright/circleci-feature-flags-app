"""
Run the Flask application.
"""

import os

from demo import create_app


def main() -> None:
    config = os.getenv("FLASK_ENV", "default")
    app = create_app(config)

    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    bind_address = os.getenv("BIND_ADDRESS", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))

    app.run(host=bind_address, port=port, debug=debug)


if __name__ == "__main__":
    main()
