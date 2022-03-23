import flask
import routes

from Common.Logger import Logger, LoggingMiddleware
from Controller import get_controller

PORT = 4000


def create_app():
    log = Logger("Starting Application")
    ctl = get_controller(log)

    flask_app = flask.Flask(__name__)
    flask_app.wsgi_app = LoggingMiddleware(log, flask_app.wsgi_app)
    flask_app = routes.add(log, flask_app, ctl)

    return flask_app


# To run in production:
# gunicorn -w 1 -b 127.0.0.1:{PORT} "app:create_app()"
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=PORT)
