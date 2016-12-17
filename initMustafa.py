import datetime
import json
import os
import psycopg2 as dbapi2
import re

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for
from flask.globals import request, current_app
from flask import Blueprint

site = Blueprint('site', __name__)
app = current_app

def initMustafaTables():
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
                
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
            
            query = """DROP TABLE IF EXISTS MESSAGE_LISTS CASCADE"""
            cursor.execute(query)
    
            query = """CREATE TABLE MESSAGE_LISTS (
                USER_ID INT,
                NAME VARCHAR(20),
                ID SERIAL PRIMARY KEY,
                FOREIGN KEY (USER_ID) REFERENCES USERS (ID) ON DELETE CASCADE
            )"""
            cursor.execute(query)
    
            query = """DROP TABLE IF EXISTS MESSAGES"""
            cursor.execute(query)
    
            query = """CREATE TABLE MESSAGES (
                LIST_ID INT,
                TEXT VARCHAR(120),
                ID SERIAL PRIMARY KEY,
                FOREIGN KEY (LIST_ID) REFERENCES MESSAGE_LISTS (ID) ON DELETE CASCADE
            )"""
            cursor.execute(query)
            
            query = """DROP TABLE IF EXISTS FOLLOW"""
            cursor.execute(query)
    
            query = """CREATE TABLE FOLLOW (
                FOLLOWER_ID INT,
                FOLLOWED_ID INT,
                PRIMARY KEY (FOLLOWER_ID, FOLLOWED_ID),
                FOREIGN KEY (FOLLOWER_ID) REFERENCES USERS (ID) ON DELETE CASCADE,
                FOREIGN KEY (FOLLOWED_ID) REFERENCES USERS (ID) ON DELETE CASCADE
            )"""
            cursor.execute(query)
        connection.commit()