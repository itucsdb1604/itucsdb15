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
from ReadBook import *
from Book import *
from _sqlite3 import Row
from builtins import str

globalBookID = 0


site = Blueprint('site', __name__)
app = current_app

def handleReadList(request):
    create_readList()
    
    if('saveButton' in request.form):
        if request.method == 'GET':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """
                        SELECT * FROM read_list;
                    """
                cursor.execute(query)
                connection.commit()
        else:
            bookName = request.form['bookName']
            readYear = request.form['readYear']
            
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """
                        SELECT id FROM book_list
                            WHERE(title = '""" + bookName + """');
                    """
                cursor.execute(query)
                connection.commit()
                id = 0
                for row in cursor.fetchall():
                    id = row[0]
                    
                newID = newIDFromReadList()
                query = """
                        INSERT INTO read_list(id, read_year, book_id)
                        VALUES("""+ str(newID) + "," + str(readYear) + "," + str(id) + """);"""
                     
                cursor.execute(query)
                connection.commit()
    
    elif('delete' in request.form):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            booksToDelete = request.form.getlist('booksToDelete')
            for id in booksToDelete:
                deleteBookFromReadList(id)
                print("ID:" + str(id))

    return getBooksFromLibrary()

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
                book.title = "https://upload.wikimedia.org/wikipedia/tr/thumb/6/61/Dijital_Kale.jpg/220px-Dijital_Kale.jpg"
            elif book.title == 'Denemeler':
                book.photo_url = "http://www.birazoku.com/wp-content/uploads/2013/01/denemeler-michel-de-montaigne.jpg"
            
        return books 


def getBooksFromReadList():
    with dbapi2.connect(app.config['dsn']) as connection:
            readbooks = list()
            cursor = connection.cursor()
            query = """
                    SELECT title, read_year, read_list.id
                        FROM book_list, read_list
                            WHERE(book_list.id = read_list.book_id)
        
                """
            cursor.execute(query)
            for row in cursor.fetchall():
                title, readYear, id = row
                newBook = ReadBook(id, title, "authorName", 2000 , readYear)
                allBooks = getBooksFromLibrary()
                for book in allBooks:
                    if book.title == title:
                        newBook.photo_url = book.photo_url
                readbooks.insert(len(readbooks), newBook)
            return readbooks 

def create_readList():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        #Creating the readlist table
        query = """
                    CREATE TABLE IF NOT EXISTS read_list(
                        id int,
                        read_year NUMERIC(4),
                        book_id int,
                        PRIMARY KEY (id)
                        );
                """
        cursor.execute(query)
        connection.commit()
    return render_template('profile.html')

def deleteBookFromReadList(id):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """
                    DELETE FROM read_list
                        WHERE (id = """ + str(id) + """);

                """
        cursor.execute(query)
        connection.commit()
    return 

def updateBookInReadList(name, newName, newAuthor, newPublishYear, newReadYear):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """
                    UPDATE read_list
                        SET book_name ="""+ newName +""", author_name ="""+ newAuthor+ """",  publish_year = """+ newPublishYear + """, read_year = """ + newReadYear +"""
                        WHERE book_name = '""" + name+ """"';
                        );
                """
        cursor.execute(query)
        connection.commit()
    return render_template('profile.html')

def newIDFromReadList():
    global globalBookID 
    globalBookID += 1
    return globalBookID
    