# uma aplicação flask é uma instância da classe flask
# tudo sobre a aplicação, como config e urls ficará aqui
# para nao termos problemas no futuro, criaremos ela dentro
# de uma função, a 'fábrica da aplicação'

# application factory
import os
from flask import Flask
from . import db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    return app