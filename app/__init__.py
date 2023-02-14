import flask
from . import tasks
from . import database
import swagger_ui


def create_app():
    app = flask.Flask(__name__)
    app.register_blueprint(tasks.blueprint)
    swagger_ui.api_doc(app, config_path='./static/openapi.yaml', title='API doc', url_prefix='/docs')
    app.add_url_rule('/', endpoint='bp_docs.swagger_blueprint_doc_handler')

    return app
