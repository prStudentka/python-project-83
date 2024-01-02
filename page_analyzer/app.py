import requests
from page_analyzer import _utils
from flask import Flask, redirect, request, render_template, flash, get_flashed_messages, url_for, g
from os import getenv
from dotenv import load_dotenv
from page_analyzer import model


load_dotenv()
__DATABASE_URL = getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')


def get_connection():
    return model.create_conn(g, __DATABASE_URL)


@app.teardown_appcontext
def close_connection(exception):
    model.close_conn(g, exception)


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@app.post('/urls')
def post_page():
    url = request.form.get('url')
    error = _utils.validate_url(url)
    if error:
        flash(error, 'danger')
        return render_template('index.html', messages=error), 422
    url_name = _utils.get_clean_url(url)
    conn = get_connection()
    res_check = model.check_url(conn, url_name)
    if not res_check:
        res_check = model.add_url(conn, url_name)
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
    id = res_check.id
    return redirect(url_for('url_id', id=id))


@app.get('/urls')
def get_urls():
    content = model.get_urls_with_checks(get_connection())
    return render_template('/urls.html', content=content)


@app.get('/urls/<int:id>')
def url_id(id):
    messages = get_flashed_messages(with_categories=True)
    conn = get_connection()
    checks = model.get_checks(conn, id)
    content = model.get_url(conn, id)
    return render_template('/url.html', content=content,
                           test=checks, messages=messages)


@app.post('/urls/<id>/checks')
def checks_id(id):
    url = model.get_url(get_connection(), id)
    try:
        req = requests.get(url.name)
        if req and (req.status_code == requests.codes.ok):
            data = _utils.get_parse_html(req)
            data['id'] = id
            model.create_check(get_connection(), data)
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'danger')
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    finally:
        return redirect(url_for('url_id', id=id))
