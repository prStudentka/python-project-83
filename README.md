### Hexlet tests and linter status:
[![Maintainability](https://api.codeclimate.com/v1/badges/d696ae2ad6630eb88f2f/maintainability)](https://codeclimate.com/github/prStudentka/python-project-83/maintainability)

[![Actions Status](https://github.com/prStudentka/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/prStudentka/python-project-83/actions)

# Page-analyzer / Анализатор страниц
website [Page Analyzer](https://page-analizer.onrender.com/)

# About / О приложении
Service for checking URLs
/ Сервис проверки веб-сайтов /

# System requirements / Системные требования
- python = "^3.10"
- flask = "^2.3.3"
- python-dotenv = "^1.0.0"
- flake8 = "^6.1.0"
- psycopg2-binary = "^2.9.9"
- validators = "^0.22.0"
- requests = "^2.31.0"
- beautifulsoup4 = "^4.12.2"
- gunicorn = "^20.1.0"
- poetry = "^1.6.1"
- postgreSQL = "^15.0"

# Install / Как запустить
1) git clone [Repository](https://github.com/prStudentka/python-project-83)
2) make install
3) created in the root directory of the project ".env" with variables:
   / создать в проекте файл ".env" c переменными:/
   - SECRET_KEY
   - DATABASE_URL
5) make start
