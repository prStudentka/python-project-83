import requests
from flask import Flask, redirect, request, render_template, flash, get_flashed_messages, url_for
from os import getenv
from dotenv import load_dotenv
from validators import url
from page_analyzer import model
from urllib.parse import urlparse
from bs4 import BeautifulSoup


__MAX_LENGTH = 255
app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = getenv('SECRET_KEY')


def validate_url(_url):
    if not _url:
        return 'URL обязателен'
    if len(_url) > __MAX_LENGTH:
        return 'URL превышает 255 символов'
    if not url(_url):
        return 'Некорректный URL'
    return ''


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


def get_clean_url(url):
    parse = urlparse(url)
    return f'{parse.scheme}://{parse.netloc}'


@app.post('/urls')
def post_page():
    url = request.form.get('url')
    error = validate_url(url)
    if error:
        flash(error, 'danger')
        return render_template('index.html', messages=error), 422

    url_name = get_clean_url(url)
    res = model.check_url(url_name)
    if not res:
        res = model.add_url(url_name)
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
    id = res[0].id
    return redirect(url_for('url_id', id=id))


@app.get('/urls')
def get_urls():
    content = []
    urls = model.get_urls()
    for _url in urls:
        id = _url.id
        name = _url.name
        check = model.find_checks(id)
        code = ''
        if check:
            code = check[0].status_code
            check = check[0].created_at
        else:
            check = ''
        content.append({'id': id, 'name': name, 'last_check': check, 'code': code})
    return render_template('/urls.html', content=content)


def get_data_by_id(id):
    data = model.find_id(id)
    content = {}
    if data:
        id, name, create_at = data
        content = {'id': id, 'name': name, 'created_at': create_at}
    return content


@app.get('/urls/<int:id>')
def url_id(id):
    messages = get_flashed_messages(with_categories=True)
    data_test = model.find_checks(id)
    content = get_data_by_id(id)
    return render_template('/page.html', content=content, test=data_test, messages=messages)


def check_empty(elem):
    if not elem or elem is None:
        return ''
    return elem


def get_parse_html(soup):
    title = soup.title.string
    h1 = []
    for elem in soup.find_all('h1'):
        if elem.string is not None:
            h1.append(elem.string)
    content = soup.select_one("meta[name='description']")['content']
    return {'h1': check_empty(h1),
            'title': check_empty(title),
            'description': check_empty(content)}


@app.post('/urls/<id>/checks')
def checks_id(id):
    url = get_data_by_id(id)
    if url:
        try:
            req = requests.get(url['name'])
        except requests.exceptions.RequestException:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('url_id', id=id))
        if req.status_code == requests.codes.ok:
            data = get_parse_html(BeautifulSoup(req.content, "html.parser"))
            model.create_check(id, req.status_code, data)
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('url_id', id=id))
