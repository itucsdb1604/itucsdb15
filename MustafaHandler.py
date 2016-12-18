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

def messageBoardHandler(listID):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if request.method == 'GET':

                query = """SELECT * FROM MESSAGES
                            WHERE (LIST_ID = %s)
                ORDER BY ID""" % listID
                cursor.execute(query)

                messages = cursor.fetchall()

                query="""SELECT USERNAME FROM USERS
                            WHERE (ID = (SELECT USER_ID FROM MESSAGE_LISTS
                                            WHERE (ID = %s)))""" % listID
                cursor.execute(query)

                userName = cursor.fetchall()

                query="""SELECT NAME FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
                cursor.execute(query)

                listName = cursor.fetchall()

                return render_template('messages.html', messages = messages, userName=userName, listName=listName, listID=listID)
            else:

                message = request.form['message']
                query = """INSERT INTO MESSAGES VALUES(%s, '%s')""" % (listID, message)
                cursor.execute(query)

                query="""SELECT USER_ID FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
                cursor.execute(query)
                userID = cursor.fetchone()
                userID = userID[0]
                
                query="""SELECT USERNAME FROM USERS
                            WHERE (ID = %s)""" % userID
                cursor.execute(query)
                userName = cursor.fetchone()
                userName = userName[0]

                query = """
                SELECT FOLLOWER_ID FROM FOLLOW
                    WHERE(FOLLOWED_ID = %s)
                """ % userID
                cursor.execute(query)
                followers = cursor.fetchall()
                
                query="""SELECT NAME FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
                cursor.execute(query)
                listName = cursor.fetchone()
                listName = listName[0]
                
                for followerid in followers:
                    query = """
                    INSERT INTO NOTIFICATION VALUES(%s, '%s has sent a new message to ''%s'' list')
                    """ % (followerid[0] ,userName, listName)
                    cursor.execute(query)

                return redirect(url_for('message_board', listID=listID))

def messageDeleteHandler(id, listID):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:

            query = "DELETE FROM MESSAGES WHERE(ID = %d)" % id
            cursor.execute(query)
            
            query="""SELECT USER_ID FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
            cursor.execute(query)
            userID = cursor.fetchone()
            userID = userID[0]
            
            query="""SELECT NAME FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
            cursor.execute(query)
            listName = cursor.fetchone()
            listName = listName[0]
            
            query = """
            SELECT FOLLOWER_ID FROM FOLLOW
                WHERE(FOLLOWED_ID = %s)
            """ % userID
            cursor.execute(query)
            followers = cursor.fetchall()
                
            query="""SELECT USERNAME FROM USERS
                            WHERE (ID = %s)""" % userID
            cursor.execute(query)
            userName = cursor.fetchone()
            userName = userName[0]
                
            for followerid in followers:
                query = """
                INSERT INTO NOTIFICATION VALUES(%s, '%s has deleted a message from %s list.')
                """ % (followerid[0] ,userName, listName)
                cursor.execute(query)

    return redirect(url_for('message_board', listID=listID))

def messageEditHandler(id, listID):
    if request.method == 'GET':
        return render_template('message_edit.html')
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """
            UPDATE MESSAGES
                SET TEXT = '%s'
                WHERE (ID = %d)
            """ % (request.form['message'], id)
            cursor.execute(query)

            query="""SELECT USER_ID FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
            cursor.execute(query)
            userID = cursor.fetchone()
            userID = userID[0]
            
            query="""SELECT NAME FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
            cursor.execute(query)
            listName = cursor.fetchone()
            listName = listName[0]
            
            query = """
            SELECT FOLLOWER_ID FROM FOLLOW
                WHERE(FOLLOWED_ID = %s)
            """ % userID
            cursor.execute(query)
            followers = cursor.fetchall()
                
            query="""SELECT USERNAME FROM USERS
                            WHERE (ID = %s)""" % userID
            cursor.execute(query)
            userName = cursor.fetchone()
            userName = userName[0]
                
            for followerid in followers:
                query = """
                INSERT INTO NOTIFICATION VALUES(%s, '%s has updated a message from %s list.')
                """ % (followerid[0] ,userName, listName)
                cursor.execute(query)
                
            connection.commit()
        return redirect(url_for('message_board', listID=listID))

def listUpdateHandler(listID):
    if request.method == 'GET':
        return render_template('list_edit.html')
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query="""SELECT NAME FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
            cursor.execute(query)
            listName = cursor.fetchone()
            oldListName = listName[0]

            listName = request.form['name']

            query = """
            UPDATE MESSAGE_LISTS
                SET NAME = '%s'
                WHERE (ID = %s)
            """ % (request.form['name'], listID)
            cursor.execute(query)

            query="""SELECT USER_ID FROM MESSAGE_LISTS
                            WHERE (ID = %s)""" % listID
            cursor.execute(query)
            userID = cursor.fetchone()
            userID = userID[0]
            
            query = """
            SELECT FOLLOWER_ID FROM FOLLOW
                WHERE(FOLLOWED_ID = %s)
            """ % userID
            cursor.execute(query)
            followers = cursor.fetchall()
                
            query="""SELECT USERNAME FROM USERS
                            WHERE (ID = %s)""" % userID
            cursor.execute(query)
            userName = cursor.fetchone()
            userName = userName[0]
                
            for followerid in followers:
                query = """
                INSERT INTO NOTIFICATION VALUES(%s, '%s has changed the name of %s list to %s')
                """ % (followerid[0] ,userName, oldListName, listName)
                cursor.execute(query)

            connection.commit()
        return redirect(url_for('signup_page'))
    
def listAddHandler(userID, userName):
    if request.method == 'GET':
        return render_template('add_list.html', userID=userID, userName=userName)

    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:

                query = """
                INSERT INTO MESSAGE_LISTS VALUES(%s, '%s')
                """ % (userID ,request.form['list_name'])
                cursor.execute(query)
                
                query = "SELECT CURRVAL('MESSAGE_LISTS_ID_SEQ')"
                cursor.execute(query)
                listID = cursor.fetchone()
                listID = listID[0]
                
                query = """
                SELECT FOLLOWER_ID FROM FOLLOW
                    WHERE(FOLLOWED_ID = %s)
                """ % userID
                cursor.execute(query)
                followers = cursor.fetchall()
                
                for followerid in followers:
                    query = """
                    INSERT INTO NOTIFICATION VALUES(%s, '%s has created a new message list.')
                    """ % (followerid[0] ,userName)
                    cursor.execute(query)

        return redirect(url_for('message_board', listID=listID))
    
def listDeleteHandler(listID):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:

            query="""SELECT NAME FROM MESSAGE_LISTS
                        WHERE (ID = %s)""" % listID
            cursor.execute(query)
            listName = cursor.fetchone()
            listName = listName[0]

            query="""SELECT USER_ID FROM MESSAGE_LISTS
                    WHERE (ID = %s)""" % listID
            cursor.execute(query)
            userID = cursor.fetchone()
            userID = userID[0]
            
            query = "DELETE FROM MESSAGE_LISTS WHERE(ID = %s)" % listID
            cursor.execute(query)
            
            query = """
            SELECT FOLLOWER_ID FROM FOLLOW
                WHERE(FOLLOWED_ID = %s)
            """ % userID
            cursor.execute(query)
            followers = cursor.fetchall()
                
            query="""SELECT USERNAME FROM USERS
                            WHERE (ID = %s)""" % userID
            cursor.execute(query)
            userName = cursor.fetchone()
            userName = userName[0]
                
            for followerid in followers:
                query = """
                INSERT INTO NOTIFICATION VALUES(%s, '%s has deleted the %s list.')
                """ % (followerid[0] ,userName, listName)
                cursor.execute(query)
            
    return redirect(url_for('signup_page'))

def followHandler(userID, userName):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            if request.method == 'GET':
                
                query="""SELECT ID, USERNAME FROM USERS"""
                cursor.execute(query)
                
                userList=cursor.fetchall()
                
                query="""SELECT FOLLOWED_ID FROM FOLLOW 
                            WHERE(FOLLOWER_ID = %s)
                      """ % userID
                cursor.execute(query)
                
                followed=cursor.fetchall()
                
                for i, f in enumerate(followed):
                    followed[i] = f[0]
                    
                followed.append(userID)
                
                return render_template('follow.html', userName=userName, userID=userID, userList=userList, followed=followed)
            else:
                ids = request.form.getlist('user_ids')
                for id in ids:
                    query="""
                        INSERT INTO FOLLOW VALUES(%d, %s)
                    """ % (userID, id)
                    cursor.execute(query)
                    
                    query = """
                    INSERT INTO NOTIFICATION VALUES(%s, '%s has followed you.')
                    """ % (id ,userName)
                    cursor.execute(query)
                    
                return redirect(url_for('users_to_follow', userID=userID, userName=userName))
            
def unfollowHandler(follower_id, followed_id):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            
            query = """DELETE FROM FOLLOW 
                        WHERE(FOLLOWER_ID = %s AND FOLLOWED_ID = %s)
                    """ % (follower_id, followed_id)
            cursor.execute(query)
            
            query="""SELECT USERNAME FROM USERS
                        WHERE(ID = %s)
                    """ % follower_id
            cursor.execute(query)
            userName = cursor.fetchone()
            userName = userName[0]
            
            query = """
                    INSERT INTO NOTIFICATION VALUES(%s, '%s has unfollowed you.')
                    """ % (followed_id ,userName)
            cursor.execute(query)
            
        return redirect(url_for('users_to_follow', userID=follower_id, userName=userName))

def notificationDeleteHandler(id):
    with dbapi2.connect(app.config['dsn']) as connection:
        with connection.cursor() as cursor:

            query = """DELETE FROM NOTIFICATION
                            WHERE(ID = %s)
                    """ % id
            cursor.execute(query)
    
    return redirect(url_for('signup_page'))

