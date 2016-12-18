import datetime
import json
import os
import psycopg2 as dbapi2
import re

from flask import Flask
from flask import current_app
from flask import request
from flask import render_template
from flask.helpers import url_for
from flask import redirect
from flask import Blueprint

site = Blueprint('site', __name__)
app = current_app

global tableCreated
tableCreated = False

def handleSignUp():
    if request.method == 'GET':
        return userList()
    else:
        if 'signup' in request.form:
            return signUp()
        elif 'delete' in request.form:
            return deleteUser()

def userList():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "SELECT * FROM USERS JOIN USERSTYPES ON (USERS.TYPEID = USERSTYPES.ID)"
        cursor.execute(query)

        u = cursor.fetchall()

        query = "SELECT * FROM MESSAGE_LISTS ORDER BY ID"
        cursor.execute(query)

        l = cursor.fetchall()
        
        query = "SELECT * FROM NOTIFICATION"
        cursor.execute(query)
        n = cursor.fetchall()
 
        query = """SELECT USER_ID, COUNT(USER_ID) FROM NOTIFICATION
                     GROUP BY USER_ID
                """
        cursor.execute(query)

        connection.commit()
    return render_template('signup.html', users = u, lists = l, notifications = n, notification_count = cursor.fetchall())

def signUp():
    username = request.form['username']
    password = request.form['password']
    type = int(request.form['type'])
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = "INSERT INTO USERS VALUES('%s', '%s', '28.11.2016', %d)" % (username, password, type)
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))

def deleteUser():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        print(request.form['delete'])

        query = "DELETE FROM USERS WHERE(ID = %s)" % request.form['delete']
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('signup_page'))

def userEdit():
    if request.method == 'GET':
        return render_template('user_edit.html')
    else:
        username = request.form['username']
        password = request.form['password']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """
            UPDATE USERS
                SET username = '%s', password = '%s' WHERE (ID = %d)
            """ % (username, password, userID)
            cursor.execute(query)
            connection.commit()
        return redirect(url_for('signup_page'))
