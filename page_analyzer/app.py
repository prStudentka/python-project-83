import requests
from flask import Flask, redirect, request, render_template, flash, get_flashed_messages, url_for
from os import getenv
from dotenv import load_dotenv
from .validate import validate_url 
from page_analyzer import model
from urllib.parse import urlparse
from bs4 import BeautifulSoup


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


def get_clean_url(url):
    parse = urlparse(url)
    return f'{parse.scheme}://{parse.netloc}'


def check_request(url):
    try:
        req = requests.get(url)
    except Exception as e:
        return e
    return req
        

@app.post('/urls')
def post_page():
    url = request.form.get('url')
    error = validate_url(url)
    if error:
        for err in error:
            flash(err, 'error')
        return render_template('index.html', messages=error), 422
    url_name = get_clean_url(url)
    res = model.check_url(url_name)
    if not res:
        res = model.add_url(url_name)
        flash('Страница успешно добавлена', 'success')
    return redirect('/urls', code=302)


@app.get('/urls')
def get_urls():
    content = model.get_urls()
    return render_template('/urls.html', content=content)


def get_data_by_id(id):
    data = model.find_id(id)
    content = {}
    if data:
        id, name, create_at = data
        content = {'id':id, 'name': name, 'created_at': create_at}
    return content


@app.get('/urls/<int:id>')
def url_id(id):
    data_test = model.find_checks(id)
    content = get_data_by_id(id)
    return render_template('/page.html', content = content, test = data_test)


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
        except Exception as e:
            print('exception!!!', e)
            return redirect(url_for('url_id', id=id))
        if req.status_code == requests.codes.ok:
            data = get_parse_html(BeautifulSoup(req.content, "html.parser")) 
            data_test = model.create_check(id, req.status_code, data)
    return redirect(url_for('url_id', id=id))

