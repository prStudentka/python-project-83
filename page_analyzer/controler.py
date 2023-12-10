from validators import url
from urllib.parse import urlparse


__MAX_LENGTH = 255


def validate_url(_url):
    if not _url:
        return 'URL обязателен'
    if len(_url) > __MAX_LENGTH:
        return 'URL превышает 255 символов'
    if not url(_url):
        return 'Некорректный URL'
    return ''


def check_empty(elem):
    if not elem or elem is None:
        return ''
    return elem


def cut_text(text):
    if len(text) > __MAX_LENGTH:
        __tmp = text
        text = __tmp[: __MAX_LENGTH - 3] + '...'
    return text


def get_clean_url(url):
    parse = urlparse(url)
    return f'{parse.scheme}://{parse.netloc}'


def get_parse_html(soup):
    title = check_empty(soup.title)
    if title:
        title = title.string
    h1 = []
    for elem in soup.find_all('h1'):
        if check_empty(elem):
            h1.append(elem.string)
    content = soup.select_one("meta[name='description']")
    content = check_empty(content)
    if content:
        content = content['content']
        content = cut_text(content)
    return {'h1': check_empty(h1),
            'title': title,
            'description': content}
