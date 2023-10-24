from flask import Flask, redirect, request, render_template, flash, get_flashed_messages, url_for
import os
import requests
from .validate import validate_url 
from page_analyzer import model
from urllib.parse import urlparse


app = Flask(__name__)


#DATABASE_URL =  os.getenv('DATABASE_URL')


@app.route('/')
def index():
    #messages = get_flashed_messages(with_categories=True)
    messages = 'hello'
    return render_template('index.html', messages = messages)


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
        #flash(error, 'error')
        return render_template('/', error=error), 422
    url_name = get_clean_url(url)
    res = model.check_url(url_name)
    if not res:
        res = model.add_url(url_name)

    #flash('Страница успешно добавлена', 'success')
    return redirect('/urls', code=302)


@app.get('/urls')
def get_urls():
    content = model.get_urls()
    return render_template('/urls.html', content=content)


@app.get('/urls/<int:id>')
def url_id(id):
    data = model.find_id(id)
    data_test = model.find_checks(id)
    content = {}
    if data:
        id, name, create_at = data
        content = {'id':id, 'name': name, 'created_at': create_at}
    return render_template('/page.html', content = content, test = data_test)


@app.post('/urls/<id>/checks')
def checks_id(id):
    #req = check_request(url_name)
    data_test = model.create_check(id)
    return redirect(url_for('url_id', id=id))

