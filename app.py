from flask import Flask
import time
import routes
import os

if __name__ == '__main__':
    app = Flask(__name__)
    bp_public = routes.create_routes()
    app.register_blueprint(bp_public, url_prefix='/v1/nurture')
    # server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    # server.serve_forever()+
    app.run('0.0.0.0', debug=False)
