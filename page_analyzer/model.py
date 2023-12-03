import psycopg2
from os import getenv
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor
from datetime import date


load_dotenv()
DATABASE_URL = getenv('DATABASE_URL')
DESCRIPTION_LIMIT = 255


def get_urls():
    connct = psycopg2.connect(DATABASE_URL)
    cursor = connct.cursor(cursor_factory=NamedTupleCursor)
    cursor.execute('SELECT * FROM urls ORDER BY id DESC;')
    result = cursor.fetchall()
    connct.commit()
    cursor.close()
    connct.close()
    return result


def check_url(name_url):
    connct = psycopg2.connect(DATABASE_URL)
    cursor = connct.cursor(cursor_factory=NamedTupleCursor)
    query = f"SELECT id, name FROM urls WHERE name = '{name_url}';"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connct.close()
    return result


def add_url(name_url):
    connct = psycopg2.connect(DATABASE_URL)
    cursor = connct.cursor(cursor_factory=NamedTupleCursor)
    date_now = date.today()
    cursor.execute('''INSERT INTO urls (name, created_at)
                      VALUES (%s, %s);''', (name_url, date_now))
    connct.commit()
    cursor.close()
    connct.close()
    result = check_url(name_url)
    return result


def find_id(data_id):
    connct = psycopg2.connect(DATABASE_URL)
    cursor = connct.cursor(cursor_factory=NamedTupleCursor)
    query = "SELECT * FROM urls WHERE id = %s;"
    cursor.execute(query, (data_id,))
    result = cursor.fetchall()
    cursor.close()
    connct.close()
    if result:
        result = result[0]
    return result


def find_checks(id):
    connct = psycopg2.connect(DATABASE_URL)
    cursor = connct.cursor(cursor_factory=NamedTupleCursor)
    query = '''SELECT * FROM url_checks WHERE url_id = %s
               ORDER BY id DESC;'''
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    cursor.close()
    connct.close()
    return result


def create_check(id, code=200, data={}):
    connct = psycopg2.connect(DATABASE_URL)
    cursor = connct.cursor(cursor_factory=NamedTupleCursor)
    date_now = date.today()
    if not data:
        data = {'h1': '', 'title': '', 'description': ''}
    if len(data['description']) > DESCRIPTION_LIMIT:
        text = data['description']
        data['description'] = text[: DESCRIPTION_LIMIT - 3] + '...'
    query = '''INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)
               VALUES (%s, %s, %s, %s, %s, %s);'''
    cursor.execute(query, (id, code, data['h1'], data['title'], data['description'], date_now))
    connct.commit()
    cursor.close()
    connct.close()
    result = find_checks(id)
    return result
