import datetime
import json
import os
import psycopg2 as dbapi2
import re


from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for

app = Flask(__name__)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


@app.route('/')
def home_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "SELECT * FROM ANNOUNCEMENTS"
        cursor.execute(query)
        connection.commit()

    return render_template('home.html', announcements = cursor.fetchall())

@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS COUNTER"""
        cursor.execute(query)

        query = """CREATE TABLE COUNTER (N INTEGER)"""
        cursor.execute(query)

        query = """INSERT INTO COUNTER (N) VALUES (0)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS ANNOUNCEMENTS"""
        cursor.execute(query)

        query = """CREATE TABLE ANNOUNCEMENTS (ID INTEGER, CONTENT VARCHAR(200))"""
        cursor.execute(query)

        query = """INSERT INTO ANNOUNCEMENTS VALUES (1, 'This is the first Announcement')"""
        cursor.execute(query)

        query = """INSERT INTO ANNOUNCEMENTS VALUES (2, 'This is the second Announcement')"""
        cursor.execute(query)

        query = """INSERT INTO ANNOUNCEMENTS VALUES (3, 'This is the third Announcement')"""
        cursor.execute(query)

        query = """INSERT INTO ANNOUNCEMENTS VALUES (4, 'This is the fourth Announcement')"""
        cursor.execute(query)

        #This Insert query is temporary
        #It will be corrected in the following commits
        query = """DROP TABLE IF EXISTS read_list"""
        cursor.execute(query)

        #Creating the readlist table
        query = """
                    CREATE TABLE read_list(
                        book_id int,
                        book_name varchar,
                        pages int
                        );
                """
        cursor.execute(query)
        #Creating the readlist table

        query = """DROP TABLE IF EXISTS WRITER"""
        cursor.execute(query)

        query = """CREATE TABLE WRITER
                        (Name VARCHAR(255),
                        OLD INTEGER,
                        MOST_POPULAR_BOOK VARCHAR(255))"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS users"""
        cursor.execute(query)
        query = """CREATE TABLE users(
                    name VARCHAR(30),
                    location VARCHAR(20),
                    birthday VARCHAR(8),
                    username VARCHAR(20) PRIMARY KEY,
                    password VARCHAR(20) NOT NULL )"""
        cursor.execute(query)

        #initialize the book table
        query = """DROP TABLE IF EXISTS BOOK"""
        cursor.execute(query)

        #Creating the book table
        query = """CREATE TABLE IF NOT EXISTS BOOK
            (
                id int,
                title varchar(60),
                isbn varchar(20),
                edition int
            )
        """
        cursor.execute(query)

        query = """INSERT INTO BOOK VALUES (1,'Tutunamayanlar','1234-5678-910',1)"""
        cursor.execute(query)
        query = """INSERT INTO BOOK VALUES (2,'Korkuyu Beklerken','1234-5678-911',1)"""
        cursor.execute(query)
        query = """INSERT INTO BOOK VALUES (3,'Tehlikeli Oyunlar','1234-5678-912',1)"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))

@app.route('/count')
def counter_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "UPDATE COUNTER SET N = N + 1"
        cursor.execute(query)
        connection.commit()

        query = "SELECT N FROM COUNTER"
        cursor.execute(query)
        count = cursor.fetchone()[0]
    return "This page was accessed %d times." % count

@app.route('/profile')
def profile_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        #This Insert query is temporary
        #It will be corrected in the following commits
        query = """
                    INSERT INTO read_list(book_id, book_name, pages)
                    VALUES(1, 'Test Book', 216);
                """
        cursor.execute(query)
        connection.commit()
    return render_template('profile.html')

@app.route('/timeline')
def timeline_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """INSERT INTO WRITER VALUES
                        ('NAZIM HIKMET', 60,
                        'PIRAYEYE MEKTUPLAR')"""
        cursor.execute(query)

    connection.commit()
    return render_template('timeline.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """INSERT INTO users VALUES('Taha', 'istanbul', '20121994', 'tahacorbaci' , '12345')"""
        cursor.execute(query)

    connection.commit()
    return render_template('signup.html')

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True


        VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='postgres' password='1234'
                               host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)
