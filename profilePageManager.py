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
        print('Save Clicked')
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
                        SELECT id FROM book
                            WHERE(title = '""" + bookName + """');
                    """
                cursor.execute(query)
                connection.commit()
                for row in cursor.fetchall():
                    id = row[0]
                    
                print(readYear)
                newID = newIDFromReadList()
                query = """
                        INSERT INTO read_list(id, read_year, book_id)
                        VALUES("""+ str(newID) + "," + str(readYear) + "," + str(id) + """);"""
                     
                cursor.execute(query)
                connection.commit()
    
    elif('delete' in request.form):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            print('Delete Button Clicked')
            booksToDelete = request.form.getlist('booksToDelete')
            for id in booksToDelete:
                deleteBookFromReadList(id)

    return getBooksFromLibrary()

def getBooksFromLibrary():
    with dbapi2.connect(app.config['dsn']) as connection:
            books = list()
            cursor = connection.cursor()
            query = """
                    SELECT * FROM book;
                """
            cursor.execute(query)
            for row in cursor.fetchall():
                id, bookName, isbn, edition, publisher = row
                books.insert(len(books), Book(id,bookName, isbn, edition))
            
            return books 


def getBooksFromReadList():
    with dbapi2.connect(app.config['dsn']) as connection:
            books = list()
            cursor = connection.cursor()
            query = """
                    SELECT title, read_year
                        FROM book, read_list
                            WHERE(book.id = read_list.book_id)
        
                """
            cursor.execute(query)
            for row in cursor.fetchall():
                title, readYear = row
                books.insert(len(books), ReadBook(1, title, "authorName", 2000 , readYear))
            
            return books 

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
    