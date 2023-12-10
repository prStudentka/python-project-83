from psycopg2.extras import NamedTupleCursor
from datetime import date


DESCRIPTION_LIMIT = 255
__STATUS_CODE = 200
NTC = NamedTupleCursor


def get_urls(connct):
    with connct.cursor(cursor_factory=NTC) as cursor:
        query = "SELECT * FROM urls ORDER BY id DESC;"
        cursor.execute(query)
        result = cursor.fetchall()
        connct.commit()
    return result


def check_url(connct, name_url):
    with connct.cursor(cursor_factory=NTC) as cursor:
        query = "SELECT id, name FROM urls WHERE name = %s;"
        cursor.execute(query, (name_url,))
        result = cursor.fetchall()
    return result


def add_url(connct, name_url):
    with connct.cursor(cursor_factory=NTC) as cursor:
        date_now = date.today()
        query = '''INSERT INTO urls (name, created_at)
                   VALUES (%s, %s);'''
        cursor.execute(query, (name_url, date_now,))
        connct.commit()
    result = check_url(connct, name_url)
    return result


def find_id(connct, data_id):
    with connct.cursor(cursor_factory=NTC) as cursor:
        query = "SELECT * FROM urls WHERE id = %s;"
        cursor.execute(query, (data_id,))
        result = cursor.fetchall()
    if result:
        result = result[0]
    return result


def find_checks(connct, id):
    with connct.cursor(cursor_factory=NTC) as cursor:
        query = '''SELECT * FROM url_checks WHERE url_id = %s
                   ORDER BY id DESC;'''
        cursor.execute(query, (id,))
        result = cursor.fetchall()
    return result


def create_check(connct, id, data={}):
    with connct.cursor(cursor_factory=NTC) as cursor:
        date_now = date.today()
        query = '''INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s);'''
        cursor.execute(query, (id, __STATUS_CODE, data['h1'], data['title'], data['description'], date_now))
        connct.commit()
    result = find_checks(connct, id)
    return result
