import psycopg2
from psycopg2.extras import NamedTupleCursor


def create_conn(g, DATABASE_URL):
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = psycopg2.connect(DATABASE_URL)
    return conn


def close_conn(g, exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()


def get_urls(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = "SELECT * FROM urls ORDER BY id DESC;"
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
    return result


def check_url(conn, name_url):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = "SELECT id, name FROM urls WHERE name = %s;"
        cursor.execute(query, (name_url,))
        result = cursor.fetchone()
    return result


def add_url(conn, name_url):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = '''INSERT INTO urls (name)
                   VALUES (%s) RETURNING id;'''
        cursor.execute(query, (name_url, ))
        conn.commit()
        result = cursor.fetchone()
    return result


def find_id(conn, data_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = "SELECT * FROM urls WHERE id = %s;"
        cursor.execute(query, (data_id,))
        result = cursor.fetchone()
    return result


def find_checks(conn, id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = '''SELECT * FROM url_checks WHERE url_id = %s
                   ORDER BY id DESC;'''
        cursor.execute(query, (id,))
        result = cursor.fetchall()
    return result


def create_check(conn, data={}):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = '''INSERT INTO url_checks (url_id, status_code, h1, title, description)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id;'''
        cursor.execute(query, (data['id'], data['code'], data['h1'], data['title'], data['description']))
        conn.commit()
        result = cursor.fetchone()
    return result
