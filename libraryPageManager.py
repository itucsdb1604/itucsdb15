import datetime
import json
import os
import psycopg2 as dbapi2
import re

from flask import Flask
from flask import current_app
from flask import request
from flask import render_template
from flask import redirect
from flask import Blueprint
from flask.helpers import url_for
from Book import *
from _sqlite3 import Row
from builtins import str


site = Blueprint('site', __name__)
app = current_app

def handleBookList(request):
    create_bookList()
    if('save' in request.form):
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            publishYear = request.form['publishYear']
            description = request.form['description']
            publisherName = request.form['publisherName']
            isbn = request.form['isbn']
            edition = request.form['edition']

            
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                
                newID = newIDFromBookList()
                print (type(newID))
                print (type(title))
                print (type(author))
                print (type(publishYear))
                print (type(description))
                print (type(publisherName))
                print (type(isbn))
                print (type(edition))

                query = """
                        INSERT INTO book_list(id, title, author, publish_year, description,
                        publisher_name, isbn, edition)
                        VALUES(%s, '%s', '%s', %s, '%s', '%s', %s, %s)""" % (newID, title, author, publishYear, description, publisherName,isbn, edition)
                cursor.execute(query)
                connection.commit()
    
    return getBooksFromLibrary()


def create_bookList():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        #Creating the book_list table
        query = """
                    CREATE TABLE IF NOT EXISTS book_list(
                        id int,
                        title varchar(60),
                        author varchar(40),
                        publish_year NUMERIC(4),
                        description varchar(200),
                        publisher_name varchar(40),
                        isbn varchar(20),
                        edition int,
                        PRIMARY KEY (id)
                        );
                """
        cursor.execute(query)
        connection.commit()
    return render_template('profile.html')

def getBooksFromLibrary():
    with dbapi2.connect(app.config['dsn']) as connection:
        books = list()
        cursor = connection.cursor()
        query = """
                SELECT * FROM book_list;
            """
        cursor.execute(query)
        for row in cursor.fetchall():
            id, title, author, publishYear, description, publisher, isbn, edition = row
            books.insert(len(books), Book(id, title, author, publishYear, description, publisher, isbn, edition))
            
        for book in books:
            if book.title == 'Hobbit':
                book.photo_url = "https://cdn.pastemagazine.com/www/system/images/photo_albums/hobbit-book-covers/large/photo_5653_0-7.jpg?1384968217"
            elif book.title == 'Tutunamayanlar':
                book.photo_url = "http://yazarokur.com/rsm/kitap/_ko/tutunamayanlar.jpg"
            elif book.title == "Korkuyu Beklerken":
                book.photo_url = "http://www.iletisim.com.tr/images/UserFiles/images/Spot/120402153824.jpg"
            elif book.title == 'Dijital Kale':
                book.photo_url = "https://upload.wikimedia.org/wikipedia/tr/thumb/6/61/Dijital_Kale.jpg/220px-Dijital_Kale.jpg"
            elif book.title == 'Denemeler':
                book.photo_url = "http://www.birazoku.com/wp-content/uploads/2013/01/denemeler-michel-de-montaigne.jpg"
            
        return books 


def newIDFromBookList():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """
                SELECT * FROM book_list;
            """
        cursor.execute(query)
        newId = 1
        for row in cursor.fetchall():
            newId += 1

        return newId

