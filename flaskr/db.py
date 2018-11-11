# aqui criamos uma conexão com o sqlite, qualquer query
# e operação feita no banco será feita utilizando
# essa conexão, que é finalizada depois de terminado o trabalho.

# em aplicações web, a conexão está tipicamente ligada a uma requisição.
# ela é criada em algum ponto quando lidamos com a requisição e fechada
# quando ela é terminada

import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# aqui definimos um comando para o terminal, 'init-db',
# que chhama a função init_db e mostra uma mensagem de 
# sucesso.

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# para usarmos nossas funções definidas inicialmente, 
# precisamos registrá-las na instância da aplicação,
# porém, como estamos utilizando uma factory function,
# a instância não está disponível para outras funções.
# inves disso, criamos a função que receba a aplicação
# e faz o registro.