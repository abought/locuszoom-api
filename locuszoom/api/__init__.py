import os, datetime
from flask import Flask, g
from flask.ext.cors import CORS
from flask.ext.cache import Cache
from raven.contrib.flask import Sentry
from locuszoom.api.json import CustomJSONEncoder

sentry = None

def create_app():
  # Create flask app
  app = Flask(__name__)

  # Which config to use
  lzapi_mode = os.environ.get("LZAPI_MODE")
  if lzapi_mode is None:
    raise Exception("No API mode designated. Set the LZAPI_MODE environment variable to 'dev' or 'prod'")

  # Config file given mode
  config_file = os.path.join(app.root_path,"../../etc/config-{}.py".format(lzapi_mode))
  if not os.path.isfile(config_file):
    raise IOError("Could not find configuration file {} for API mode {}".format(config_file,lzapi_mode))

  # Load config
  app.config.from_pyfile(config_file)

  # Set mode
  app.config["LZAPI_MODE"] = lzapi_mode

  # Start logging errors
  if "SENTRY_DSN" in app.config:
    sentry = Sentry(app,dsn=app.config["SENTRY_DSN"],register_signal=False,wrap_wsgi=False)
  else:
    print "Warning: Sentry DSN not found, skipping"

  # Enable cross-domain headers on all routes
  CORS(app)

  # Enable caching
  cache = Cache(
    app,
    config = app.config["CACHE_CONFIG"]
  )

  with app.app_context():
    # Register routes with app
    from locuszoom.api import routes
    app.register_blueprint(routes.bp)

  # JSON encoder for datetimes
  app.json_encoder = CustomJSONEncoder

  return app