import configparser

from flask import jsonify
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from operator_service.constants import BaseURLs, ConfigSections, Metadata
from operator_service.myapp import app
from operator_service.routes import services


def get_version():
    conf = configparser.ConfigParser()
    conf.read('.bumpversion.cfg')
    return conf['bumpversion']['current_version']


@app.route('/')
def version():
    info = dict()
    info['software'] = Metadata.TITLE
    info['version'] = get_version()
    return jsonify(info)


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = get_version()
    swag['info']['title'] = Metadata.TITLE
    swag['info']['description'] = Metadata.DESCRIPTION
    return jsonify(swag)


config = configparser.ConfigParser()
config.read(app.config['CONFIG_FILE'])
operator_url = config.get(ConfigSections.RESOURCES, 'operator.url')
# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    BaseURLs.SWAGGER_URL,
    operator_url + '/spec',
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
)

# Register blueprint at URL
app.register_blueprint(swaggerui_blueprint, url_prefix=BaseURLs.SWAGGER_URL)
app.register_blueprint(services, url_prefix=BaseURLs.BASE_OPERATOR_URL)

if __name__ == '__main__':
    app.run(port=8050)