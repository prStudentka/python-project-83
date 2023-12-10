import psycopg2
import requests
import page_analyzer.controler as ctr
from flask import Flask, redirect, request, render_template, flash, get_flashed_messages, url_for, g
from os import getenv
from dotenv import load_dotenv
from page_analyzer import model
from bs4 import BeautifulSoup


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
__DATABASE_URL = getenv('DATABASE_URL')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(__DATABASE_URL)
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.post('/urls')
def post_page():
    url = request.form.get('url')
    error = ctr.validate_url(url)
    if error:
        flash(error, 'danger')
        return render_template('index.html', messages=error), 422
    url_name = ctr.get_clean_url(url)
    db = get_db()
    res = model.check_url(db, url_name)
    if not res:
        res = model.add_url(db, url_name)
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
    id = res[0].id
    return redirect(url_for('url_id', id=id))


@app.get('/urls')
def get_urls():
    content = []
    db = get_db()
    urls = model.get_urls(db)
    for _url in urls:
        check = model.find_checks(db, _url.id)
        code = ''
        if check:
            code = check[0].status_code
            check = check[0].created_at
        else:
            check = ''
        content.append({'id': _url.id, 'name': _url.name, 'last_check': check, 'code': code})
    return render_template('/urls.html', content=content)


def get_data_by_id(connct, id):
    data = model.find_id(connct, id)
    content = {}
    if data:
        id, name, create_at = data
        content = {'id': id, 'name': name, 'created_at': create_at}
    return content


@app.get('/urls/<int:id>')
def url_id(id):
    messages = get_flashed_messages(with_categories=True)
    db = get_db()
    data_test = model.find_checks(db, id)
    content = get_data_by_id(db, id)
    return render_template('/url.html', content=content, test=data_test, messages=messages)


def get_page(url):
    try:
        req = requests.get(url['name'])
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return ''
    return req


@app.post('/urls/<id>/checks')
def checks_id(id):
    db = get_db()
    url = get_data_by_id(db, id)
    req = get_page(url)
    if req and (req.status_code == requests.codes.ok):
        data = ctr.get_parse_html(BeautifulSoup(req.content, "html.parser"))
        model.create_check(db, id, data)
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('url_id', id=id))
