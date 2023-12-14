import psycopg2
from psycopg2.extras import NamedTupleCursor as NTC


def create_conn(g, DATABASE_URL):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db
	

def close_conn(g, exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_urls(conn):
    with conn.cursor(cursor_factory=NTC) as cursor:
        query = '''SELECT u.id, u.name, uc.status_code, uc.created_at FROM urls u 
                   FULL JOIN url_checks uc ON u.id =uc.url_id
                   WHERE uc.created_at is NULL or uc.created_at = (
				        SELECT MAX(created_at) 
		                FROM url_checks 
		                WHERE url_id = u.id)
                   GROUP BY (u.id,u.name, uc.status_code, uc.created_at)   
                   ORDER BY u.id DESC;'''
        cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
    return result


def check_url(conn, name_url):
    with conn.cursor(cursor_factory=NTC) as cursor:
        query = "SELECT id, name FROM urls WHERE name = %s;"
        cursor.execute(query, (name_url,))
        result = cursor.fetchall()
    return result


def add_url(conn, name_url):
    with conn.cursor(cursor_factory=NTC) as cursor:
        query = '''INSERT INTO urls (name, created_at)
                   VALUES (%s, NOW());'''
        cursor.execute(query, (name_url, ))
        conn.commit()
    result = check_url(conn, name_url)
    return result


def find_id(conn, data_id):
    with conn.cursor(cursor_factory=NTC) as cursor:
        query = "SELECT * FROM urls WHERE id = %s;"
        cursor.execute(query, (data_id,))
        result = cursor.fetchone()
    return result


def find_checks(conn, id):
    res_test = [find_id(conn, id)]
    with conn.cursor(cursor_factory=NTC) as cursor:
        query = '''SELECT * FROM url_checks WHERE url_id = %s
                   ORDER BY id DESC;'''
        cursor.execute(query, (id,))
        result = cursor.fetchall()
    res_test.append(result)
    return res_test


def create_check(conn, data={}):
    with conn.cursor(cursor_factory=NTC) as cursor:
        query = '''INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)
                   VALUES (%s, %s, %s, %s, %s, current_timestamp);'''
        cursor.execute(query, (data['id'], data['code'], data['h1'], data['title'], data['description']))
        conn.commit()
    result = find_checks(conn, data['id'])
    return result
