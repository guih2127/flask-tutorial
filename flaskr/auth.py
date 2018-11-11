import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# criamos uma blueprinth noemada de auth, a url_prefix
# definida será extendida para todas as url
# associadas com essa blueprint

@bp.route('/register', methods=('GET', 'POST')) # associa a função register com a url /register
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Por favor, digite um usuário.'
        elif not password:
            error = 'Por favor, digite uma senha.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'Usuário {} já está registrado.'.format(username)

            # aqui validamos que username e password estão presente,
            # verificamos também se o usuário não existe, com o ultimo elif
    
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

                # se não existir nenhum erro, o registro será feito
        
        flash(error)

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if username is None:
            error = 'Usuário inválido, tente novamente.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta, tente novamente.'

            # com check_password_hash comparamos o password digitado
            # que guardamos a hash digitada no cadastro
        
        if error is None:
            session.clear()
            session['user_id'] = user['id'] 
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')

            # session é um dicionário que guarda dados entre as requisições
            # se o usuário logar com sucesso, seu id será guardado em uma nova
            # session. esse id estará disponível para outras requests

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        )

        # before_app_request registra uma função que roda antes da função view,
        # não importa qual URL seja requisitada, a função load_logged_in_user
        # obtem o user_id guardado na session e, então, obtém os dados do
        # usuário no banco de dados, guardando estes dados em g.user, que estará
        # disponível durante a requisição

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

    # para criarmos o logout, removemos o user_id da session, então
    # a função load_logged_in_user não irá carregar o user nas
    # próximas requests

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

    # criamos a view login_required, que possui dentro dela
    # um decorator que retorna uma nova view que envolta a view original.
    # a nova função verifica se o usuario está logado e, se não, redireciona
    # para a página de login. se o usuário estiver logado a view é chamada
    # normalmente 


