import datetime
import json
import os
import psycopg2 as dbapi2
import re


from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for
from flask.globals import request
from profilePageManager import *
from MustafaHandler import *
from initMustafa import *

app = Flask(__name__)

global userID
userID = 0
global key
key = 0
global ckey
ckey = 0
global akey
akey = 0

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

        query = """DROP TABLE IF EXISTS AWARDS CASCADE"""
        cursor.execute(query)
        
        query = """DROP TABLE IF EXISTS WRITERS CASCADE"""
        cursor.execute(query)  
        
        query = """DROP TABLE IF EXISTS CATEGORIES CASCADE"""
        cursor.execute(query)
        
        query = """CREATE TABLE CATEGORIES
                        (name VARCHAR(40),
                        feature VARCHAR(40),
                        ckey INTEGER PRIMARY KEY)"""
        cursor.execute(query)
        
        query = """INSERT INTO CATEGORIES VALUES ('Poem','Literary',1)"""
        cursor.execute(query)
        query = """INSERT INTO CATEGORIES VALUES ('Novel','Classic',2)"""
        cursor.execute(query)
        query = """INSERT INTO CATEGORIES VALUES ('Magazine','Intriguing',3)"""
        cursor.execute(query)
        
        query = """CREATE TABLE WRITERS
                        (name VARCHAR(40),
                        age VARCHAR(10),
                        key INTEGER PRIMARY KEY,
                        categoryid INTEGER,
                        FOREIGN KEY (categoryid) REFERENCES CATEGORIES (ckey))"""
        cursor.execute(query)
        
        query = """INSERT INTO WRITERS VALUES ('Orhan Veli Kanik','45',1,1)"""
        cursor.execute(query)
        query = """INSERT INTO WRITERS VALUES ('Orhan Pamuk','55',2,2)"""
        cursor.execute(query)        
        query = """INSERT INTO WRITERS VALUES ('Atilla Ilhan','65',3,1)"""
        cursor.execute(query)   
        
        query = """CREATE TABLE AWARDS
                        (name VARCHAR(40),
                        year VARCHAR(4),
                        akey INTEGER PRIMARY KEY,
                        writerid INTEGER,
                        FOREIGN KEY (writerid) REFERENCES WRITERS (key))"""
        cursor.execute(query)

        query = """INSERT INTO AWARDS VALUES ('Best Poem Of Year','2015',1,1)"""
        cursor.execute(query)
        query = """INSERT INTO AWARDS VALUES ('Best Novel Of Year','2013',2,2)"""
        cursor.execute(query)         

        query = """DROP TABLE IF EXISTS USERSTYPES CASCADE"""
        cursor.execute(query)
        query = """CREATE TABLE USERSTYPES(
                    id INTEGER PRIMARY KEY,
                    type VARCHAR(20),
                    readright boolean,
                    writeright boolean )"""
        cursor.execute(query)

        query = """INSERT INTO USERSTYPES VALUES(0, 'Admin', TRUE, TRUE)"""
        cursor.execute(query)
        query = """INSERT INTO USERSTYPES VALUES(1, 'Member', TRUE, FALSE)"""
        cursor.execute(query)
        query = """INSERT INTO USERSTYPES VALUES(2, 'Guest', FALSE, FALSE)"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)
        query = """CREATE TABLE USERS(
                    ID INTEGER PRIMARY KEY,
                    username VARCHAR(20) NOT NULL,
                    password VARCHAR(20) NOT NULL,
                    joindate VARCHAR(20),
                    typeid INTEGER,
                    FOREIGN KEY (typeid) REFERENCES USERSTYPES(id) ON DELETE RESTRICT )"""
        cursor.execute(query)

        #initialize the PUBLISHER table -Ufuk SAHAR-
        query = """DROP TABLE IF EXISTS PUBLISHER CASCADE"""
        cursor.execute(query)
        #initialize the BOOK table
        query = """DROP TABLE IF EXISTS BOOK"""
        cursor.execute(query)
        #Creating the PUBLISHER table
        query = """CREATE TABLE IF NOT EXISTS PUBLISHER
            (
                id int PRIMARY KEY,
                name varchar(40)
            )
        """
        cursor.execute(query)
        query = """INSERT INTO PUBLISHER VALUES (1,'ABC')"""
        cursor.execute(query)
        query = """INSERT INTO PUBLISHER VALUES (2,'XYZ')"""
        cursor.execute(query)
        query = """INSERT INTO PUBLISHER VALUES (3,'PQR')"""
        cursor.execute(query)

        #Creating the book table
        query = """CREATE TABLE IF NOT EXISTS BOOK
            (
                id int,
                title varchar(60),
                isbn varchar(20),
                edition int,
                publisher_id int,
                FOREIGN KEY (publisher_id) REFERENCES PUBLISHER(id),
                PRIMARY KEY (id)
            )
        """
        cursor.execute(query)

        query = """INSERT INTO BOOK VALUES (1,'Tutunamayanlar','1234-5678-910',1,3)"""
        cursor.execute(query)
        query = """INSERT INTO BOOK VALUES (2,'Korkuyu Beklerken','1234-5678-911',1,1)"""
        cursor.execute(query)
        query = """INSERT INTO BOOK VALUES (3,'Tehlikeli Oyunlar','1234-5678-912',1,2)"""
        cursor.execute(query)
        connection.commit()

        #creating the massages table - Mustafa Furkan Suve
        initMustafaTables()

    return redirect(url_for('home_page'))

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    bookList = handleReadList(request)
    readBooks = getBooksFromReadList()
    return render_template('profile.html', readbooks = readBooks, booklist = bookList, size = len(readBooks))

@app.route('/timeline')
def timeline_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    connection.commit()
    return render_template('timeline.html')

@app.route('/follow/<int:userID>/<userName>', methods=['GET', 'POST'])
def users_to_follow(userID, userName):
    return followHandler(userID, userName)

@app.route('/unfollow/<follower_id>/<followed_id>')
def unfollow(follower_id, followed_id):
    return unfollowHandler(follower_id, followed_id)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/delete_list/<listID>')
def list_delete(listID):
    return listDeleteHandler(listID)

@app.route('/update_list/<listID>', methods=['GET', 'POST'])
def list_update(listID):
    return listUpdateHandler(listID)

@app.route('/add_list/<userID>/<userName>', methods=['GET', 'POST'])
def list_add(userID, userName):
    return listAddHandler(userID, userName)
    
@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM USERS JOIN USERSTYPES ON (USERS.TYPEID = USERSTYPES.ID)"
            cursor.execute(query)

            u = cursor.fetchall()

            query = "SELECT * FROM MESSAGE_LISTS ORDER BY ID"
            cursor.execute(query)

            l = cursor.fetchall()

            connection.commit()
        return render_template('signup.html', users = u, lists = l)
    else:
        if 'signup' in request.form:
            username = request.form['username']
            password = request.form['password']
            type = int(request.form['type'])
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                global userID
                query = "INSERT INTO USERS VALUES('%d', '%s', '%s', '28.11.2016', '%d')" % (userID, username, password, type)
                cursor.execute(query)
                userID = userID + 1
                connection.commit()
            return redirect(url_for('signup_page'))
        elif 'delete' in request.form:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                print(request.form['delete'])

                query = "DELETE FROM USERS WHERE(ID = %s)" % request.form['delete']
                cursor.execute(query)

                connection.commit()
            return redirect(url_for('signup_page'))

@app.route('/user/edit<int:userID>', methods=['GET', 'POST'])
def user_edit(userID):
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

@app.route('/adminsettings', methods=['GET', 'POST'])
def admin_setting():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM USERSTYPES ORDER BY ID"
            cursor.execute(query)

            connection.commit()
        return render_template('adminsettings.html', types = cursor.fetchall())
    else:
        if 'admin' in request.form:
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
        elif 'admin_delete' in request.form:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "DELETE FROM USERSTYPES WHERE(ID = 0)"
                cursor.execute(query)
                connection.commit()
            return redirect(url_for('signup_page'))
        elif 'member' in request.form:
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
        elif 'member_delete' in request.form:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "DELETE FROM USERSTYPES WHERE(ID = 1)"
                cursor.execute(query)
                connection.commit()
            return redirect(url_for('signup_page'))
        elif 'guest' in request.form:
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
        elif 'guest_delete' in request.form:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = "DELETE FROM USERSTYPES WHERE(ID = 2)"
                cursor.execute(query)
                connection.commit()
            return redirect(url_for('signup_page'))

@app.route('/messages/edit<int:id>/<listID>', methods=['GET', 'POST'])
def message_edit(id, listID):
    return messageEditHandler(id, listID)

@app.route('/messages/<listID>', methods=['GET', 'POST'])
def message_board(listID):
    return messageBoardHandler(listID)

@app.route('/message/delete<int:id>/<listID>', methods=['GET', 'POST'])
def message_delete(id, listID):
    return messageDeleteHandler(id, listID)

global bookID
bookID=4
global publisherID

@app.route('/library', methods=['GET', 'POST'])
def library_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM BOOK JOIN PUBLISHER ON BOOK.PUBLISHER_ID=PUBLISHER.ID ORDER BY BOOK.ID  "
            cursor.execute(query)

            connection.commit()
        return render_template('library.html',books = cursor.fetchall())


    else:
        title = request.form['title']
        publishername = request.form['publishername']
        isbn = request.form['isbn']
        edition = request.form['edition']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            publisherID=1
            query = "SELECT name FROM PUBLISHER"
            cursor.execute(query)
            publishers_name = cursor.fetchall()
            print(publishers_name[0])

            for name in publishers_name:
                if name[0] == publishername:
                    break
                publisherID=publisherID+1


            print(publisherID)
            global bookID
            if name[0] != publishername:
                query = "INSERT INTO PUBLISHER VALUES(%d, '%s')" % (publisherID,publishername)
                cursor.execute(query)
            query = "INSERT INTO BOOK VALUES(%d, '%s', '%s','%s',%d)" % (bookID,title,isbn,edition,publisherID)
            cursor.execute(query)


            bookID=bookID+1;

            connection.commit()
        return redirect(url_for('library_page'))



@app.route('/writers', methods=['GET', 'POST'])
def writers_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM WRITERS ORDER BY KEY"
            cursor.execute(query)

            connection.commit()
        return render_template('writers.html', writers = cursor.fetchall())
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            
            query = "SELECT * FROM WRITERS ORDER BY KEY"
            cursor.execute(query)
            writers = cursor.fetchall()
            

            deletes = request.form.getlist('writers_to_delete')
            for delete in deletes:

                query = "DELETE FROM WRITERS WHERE KEY='%s'" %delete
                cursor.execute(query)
                
            query = "SELECT * FROM WRITERS ORDER BY KEY"
            cursor.execute(query)
            writers = cursor.fetchall()
            
            connection.commit()
        return render_template('writers.html', writers = writers)

@app.route('/writer/<int:key>')
def writer_page(key):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        
    query = "SELECT * FROM AWARDS WHERE WRITERID = '%d'" %key 
    cursor.execute(query)

    awards = cursor.fetchall()

    query = "SELECT * FROM WRITERS WHERE KEY ='%d'" %key
    cursor.execute(query)

    writers = cursor.fetchall()
    for writer in writers:
        if writer[2] == key:
            return render_template('writer.html', writer = writer, awards = awards)

@app.route('/writers/add', methods=['GET', 'POST'])
def writer_add_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "SELECT * FROM CATEGORIES ORDER BY CKEY"
        cursor.execute(query)
        categories = cursor.fetchall()

    if request.method == 'GET':
        form = {'name', 'age','categoryid'}
        connection.commit()
        return render_template('writer_edit.html',categories = categories,form=form)
    else:
        name = request.form['name']
        age = request.form['age']
        categoryid = int(request.form['categoryid'])
        
        query = "SELECT * FROM WRITERS ORDER BY KEY "
        cursor.execute(query)
        
        writers = cursor.fetchall()
        global key
        
        for writer in writers:
            if writer[2] > key:
                key = writer[2]
        
        key = key + 1

        query = "INSERT INTO WRITERS VALUES('%s', '%s', '%d', %d)" % (name, age, key, categoryid)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('writer_page',  key=key))


@app.route('/writer/<int:key>/edit', methods=['GET', 'POST'])
def writer_edit_page(key):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    query = "SELECT * FROM CATEGORIES ORDER BY CKEY"
    cursor.execute(query)
    categories = cursor.fetchall()

    query = "SELECT * FROM WRITERS WHERE KEY =key"
    cursor.execute(query)


    if request.method == 'GET':
        form = {'name', 'age', 'categoryid'}
        connection.commit()
        return render_template('writer_edit.html',categories = categories, form = form)
    else:
        name = request.form['name']
        age = request.form['age']
        categoryid = int(request.form['categoryid'])

        query = "UPDATE WRITERS SET name= '%s', age='%s',categoryid ='%d' WHERE KEY='%d'" % (name, age, categoryid, key)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('writer_page', key=key))

@app.route('/categories', methods=['GET', 'POST'])
def categories_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM CATEGORIES ORDER BY CKEY"
            cursor.execute(query)

            connection.commit()
        return render_template('categories.html', categories = cursor.fetchall())
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            deletes = request.form.getlist('categories_to_delete')
            for delete in deletes:

                query = "DELETE FROM CATEGORIES WHERE CKEY='%s'" %delete
                cursor.execute(query)
            
        query = "SELECT * FROM CATEGORIES ORDER BY CKEY"
        cursor.execute(query)    
            
        connection.commit()
        return render_template('categories.html', categories = cursor.fetchall())

@app.route('/category/<int:ckey>')
def category_page(ckey):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    query = "SELECT * FROM WRITERS WHERE CATEGORYID = '%d'" %ckey
    cursor.execute(query)
    writers = cursor.fetchall()

    query = "SELECT * FROM CATEGORIES WHERE CKEY ='%d'" %ckey
    cursor.execute(query)

    categories = cursor.fetchall()
    for category in categories:
        if category[2] == ckey:
                return render_template('category.html', writers = writers, category = category)

@app.route('/categories/add', methods=['GET', 'POST'])
def category_add_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    if request.method == 'GET':
        form = {'name', 'feature'}
        connection.commit()
        return render_template('category_edit.html',form=form)
    else:
        name = request.form['name']
        feature = request.form['feature']

        query = "SELECT * FROM CATEGORIES ORDER BY CKEY "
        cursor.execute(query)
        
        categories = cursor.fetchall()
        global ckey
        
        for category in categories:
            if category[2] > ckey:
                ckey = category[2]
        
        ckey = ckey + 1

        query = "INSERT INTO CATEGORIES VALUES('%s', '%s', %d)" % (name, feature, ckey)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('category_page',  ckey=ckey))


@app.route('/category/<int:ckey>/edit', methods=['GET', 'POST'])
def category_edit_page(ckey):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    query = "SELECT * FROM CATEGORIES WHERE CKEY =ckey"
    cursor.execute(query)


    if request.method == 'GET':
        form = {'name', 'feature'}
        connection.commit()
        return render_template('category_edit.html', form = form)
    else:
        name = request.form['name']
        feature = request.form['feature']

        query = "UPDATE CATEGORIES SET name= '%s', feature='%s' WHERE CKEY='%d'" % (name, feature, ckey)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('category_page', ckey=ckey))

@app.route('/awards', methods=['GET', 'POST'])
def awards_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM AWARDS ORDER BY AKEY"
            cursor.execute(query)

            connection.commit()
        return render_template('awards.html', awards = cursor.fetchall())
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            deletes = request.form.getlist('awards_to_delete')
            for delete in deletes:
                query = "DELETE FROM AWARDS WHERE AKEY='%s'" %delete
                cursor.execute(query)
                
        query = "SELECT * FROM AWARDS ORDER BY AKEY"
        cursor.execute(query)
        connection.commit()
        return render_template('awards.html', awards = cursor.fetchall())

@app.route('/award/<int:akey>')
def award_page(akey):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        
    query = "SELECT * FROM AWARDS WHERE AKEY ='%d'" %akey
    cursor.execute(query)
    awards = cursor.fetchall()
    award = awards[0]
            
    query = "SELECT * FROM WRITERS WHERE KEY ='%d'" %award[3]
    cursor.execute(query)
    writers = cursor.fetchall()
    return render_template('award.html', award = award, writer = writers[0])

@app.route('/awards/add', methods=['GET', 'POST'])
def award_add_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "SELECT * FROM WRITERS ORDER BY KEY"
        cursor.execute(query)
        writers = cursor.fetchall()

    if request.method == 'GET':
        form = {'name', 'year','writerid'}
        connection.commit()
        return render_template('award_edit.html',writers = writers,form=form)
    else:
        name = request.form['name']
        year = request.form['year']
        writerid = int(request.form['writerid'])
        
        query = "SELECT * FROM AWARDS ORDER BY AKEY "
        cursor.execute(query)
        
        awards = cursor.fetchall()
        global akey
        
        for award in awards:
            if award[2] > akey:
                akey = award[2]
        
        akey = akey + 1

        query = "INSERT INTO AWARDS VALUES('%s', '%s', '%d', %d)" % (name, year, akey, writerid)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('award_page',  akey=akey))


@app.route('/award/<int:akey>/edit', methods=['GET', 'POST'])
def award_edit_page(akey):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    query = "SELECT * FROM WRITERS ORDER BY KEY"
    cursor.execute(query)
    writers = cursor.fetchall()

    query = "SELECT * FROM AWARDS WHERE AKEY =akey"
    cursor.execute(query)


    if request.method == 'GET':
        form = {'name', 'year', 'writerid'}
        connection.commit()
        return render_template('award_edit.html',writers = writers, form = form)
    else:
        name = request.form['name']
        year = request.form['year']
        writerid = int(request.form['writerid'])

        query = "UPDATE AWARDS SET name= '%s', year='%s',writerid ='%d' WHERE AKEY='%d'" % (name, year, writerid, akey)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('award_page', akey=akey))


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
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)
