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
from _sqlite3 import Row

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
            id = newIDFromReadList()
            bookName = request.form['bookName']
            authorName = request.form['authorName']
            publishYear = request.form['publishYear']    
            readYear = request.form['readYear']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """
                        INSERT INTO read_list(id, book_name, author_name, publish_year, read_year)
                        VALUES("""+ str(id) + ",'" + bookName  + "','" + authorName + "'," + publishYear + ',' + readYear + """);
                    """
                cursor.execute(query)
                connection.commit()
    
    elif('delete' in request.form):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            print('Delete Button Clicked')
            booksToDelete = request.form.getlist('booksToDelete')
            for id in booksToDelete:
                deleteBookFromReadList(id)

    return getBooksFromReadList()

def getBooksFromReadList():
    with dbapi2.connect(app.config['dsn']) as connection:
            books = list()
            cursor = connection.cursor()
            query = """
                    SELECT * FROM read_list;
                """
            cursor.execute(query)
            for row in cursor.fetchall():
                id, bookName, authorName, publishYear, readYear = row
                books.insert(len(books), ReadBook(id, bookName, authorName, publishYear, readYear))
            
            return books 

def create_readList():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        #Creating the readlist table
        query = """
                    CREATE TABLE IF NOT EXISTS read_list(
                        id int,
                        book_name varchar,
                        author_name varchar,
                        publish_year int,
                        read_year int
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
    