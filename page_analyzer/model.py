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


def get_url(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        query = "SELECT * FROM urls WHERE id = %s;"
        cursor.execute(query, (url_id,))
        result = cursor.fetchone()
    return result


def get_checks(conn, id):
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


def get_urls_with_checks(conn):
    content = []
    keys = ('id', 'name', 'created_at', 'status_code')
    urls = get_urls(conn)
    for _url in urls:
        check = get_checks(conn, _url.id)
        if check:
            values = (_url.id, _url.name, check[0].created_at, check[0].status_code)
        else:
            values = (_url.id, _url.name, '', '')
        content.append(dict(zip(keys, values)))
    return content
