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

def handleAdminSetting():
    if request.method == 'GET':
        return userTypeList()
    else:
        if 'admin' in request.form:
            return adminUpdate()
        elif 'admin_delete' in request.form:
            return adminDelete()
        elif 'member' in request.form:
            return memberUpdate()
        elif 'member_delete' in request.form:
            return memberDelete()
        elif 'guest' in request.form:
            return guestUpdate()
        elif 'guest_delete' in request.form:
            return guestDelete()

def userTypeList():
    with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM USERSTYPES ORDER BY ID"
            cursor.execute(query)

            connection.commit()
    return render_template('adminsettings.html', types = cursor.fetchall())

def adminUpdate():
    read = request.form['read0']
    write = request.form['write0']
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """
        UPDATE USERSTYPES
            SET readright = '%s', writeright = '%s' WHERE (ID = 0)
        """ % (read, write)
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))
def adminDelete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM USERSTYPES WHERE(ID = 0)"
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))
def memberUpdate():
    read = request.form['read1']
    write = request.form['write1']
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """
        UPDATE USERSTYPES
            SET readright = '%s', writeright = '%s' WHERE (ID = 1)
        """ % (read, write)
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))
def memberDelete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM USERSTYPES WHERE(ID = 1)"
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))
def guestUpdate():
    read = request.form['read2']
    write = request.form['write2']
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """
        UPDATE USERSTYPES
            SET readright = '%s', writeright = '%s' WHERE (ID = 2)
        """ % (read, write)
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))
def guestDelete():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = "DELETE FROM USERSTYPES WHERE(ID = 2)"
        cursor.execute(query)
        connection.commit()
    return redirect(url_for('signup_page'))