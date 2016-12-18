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
from libraryPageManager import *
from MustafaHandler import *
from initMustafa import *
from SignUpHandler import *
from AdminSettingHandler import *

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
                    username VARCHAR(20) NOT NULL,
                    password VARCHAR(20) NOT NULL,
                    joindate VARCHAR(20),
                    typeid INTEGER,
                    ID SERIAL PRIMARY KEY,
                    FOREIGN KEY (typeid) REFERENCES USERSTYPES(id) ON DELETE RESTRICT )"""
        cursor.execute(query)

        ###############    Ufuk  SAHAR    ##############
        #initialize the PUBLISHER table#
        query = """DROP TABLE IF EXISTS PUBLISHER CASCADE"""
        cursor.execute(query)
        #initialize the SELLER table#
        query = """DROP TABLE IF EXISTS SELLER CASCADE"""
        cursor.execute(query)
        #initialize the BOOK table#
        query = """DROP TABLE IF EXISTS BOOK"""
        cursor.execute(query)
        #Creating the PUBLISHER table#
        query = """CREATE TABLE IF NOT EXISTS PUBLISHER
            (
                pub_id int PRIMARY KEY,
                name varchar(40),
                phone_number varchar(20),
                address varchar(50)
            )
        """
        cursor.execute(query)
        query = """INSERT INTO PUBLISHER VALUES (1,'ABC','02122754758','Besiktas')"""
        cursor.execute(query)
        query = """INSERT INTO PUBLISHER VALUES (2,'XYZ','02122482547','Mecidiyekoy')"""
        cursor.execute(query)
        query = """INSERT INTO PUBLISHER VALUES (3,'PQR','02122472554','Sisli')"""
        cursor.execute(query)
        #Creating the SELLER table#
        query = """CREATE TABLE IF NOT EXISTS SELLER
            (
                s_isbn varchar(20) PRIMARY KEY,
                name varchar(40),
                price varchar(20),
                type varchar(20)
            )
        """
        cursor.execute(query)

        query = """INSERT INTO SELLER VALUES ('1234-5678-910','D&R','$10','OLD')"""
        cursor.execute(query)
        query = """INSERT INTO SELLER VALUES ('1234-5678-911','D&R','$20','NEW')"""
        cursor.execute(query)
        query = """INSERT INTO SELLER VALUES ('1234-5678-912','D&R','$30','NEW')"""
        cursor.execute(query)
        #Creating the book table
        query = """CREATE TABLE IF NOT EXISTS BOOK
            (
                id int,
                title varchar(60),
                isbn varchar(20),
                edition int,
                publisher_id int,
                FOREIGN KEY (publisher_id) REFERENCES PUBLISHER(pub_id),
                FOREIGN KEY (isbn) REFERENCES SELLER(s_isbn),
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

@app.route('/follow/<int:userID>/<userName>', methods=['GET', 'POST'])
def users_to_follow(userID, userName):
    return followHandler(userID, userName)

@app.route('/unfollow/<follower_id>/<followed_id>')
def unfollow(follower_id, followed_id):
    return unfollowHandler(follower_id, followed_id)

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

@app.route('/delete_notification/<id>')
def notification_delete(id):
    return notificationDeleteHandler(id)

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    return handleSignUp()

@app.route('/user/edit<int:userID>', methods=['GET', 'POST'])
def user_edit(userID):
    return userEdit(userID)

@app.route('/adminsettings', methods=['GET', 'POST'])
def admin_setting():
    return handleAdminSetting()

@app.route('/messages/edit<int:id>/<listID>', methods=['GET', 'POST'])
def message_edit(id, listID):
    return messageEditHandler(id, listID)

@app.route('/messages/<listID>', methods=['GET', 'POST'])
def message_board(listID):
    return messageBoardHandler(listID)

@app.route('/message/delete<int:id>/<listID>', methods=['GET', 'POST'])
def message_delete(id, listID):
    return messageDeleteHandler(id, listID)

global id
id=0
global publisherID
publisherID=3
@app.route('/library', methods=['GET', 'POST'])
def library_page():
    libraryBooks = handleBookList(request)
    return render_template('library.html', books = libraryBooks, size = len(libraryBooks))

@app.route('/book/<int:id>')
def book_page(id):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    query = "SELECT * FROM BOOK JOIN PUBLISHER ON PUBLISHER_ID=PUB_ID ORDER BY ID"
    cursor.execute(query)

    library = cursor.fetchall()
    for book in library:
        if book[0] == id:
                return render_template('book.html', book = book)



@app.route('/library/add', methods=['GET', 'POST'])
def book_add_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    if request.method == 'GET':
        form = {'title','publishername', 'isbn','edition'}
        connection.commit()
        return render_template('book_edit.html',form=form,is_add=1)
    else:
        title = request.form['title']
        publishername = request.form['publishername']
        isbn = request.form['isbn']
        edition = request.form['edition']
        global id
        publisherID=1
        query = "SELECT * FROM PUBLISHER"
        cursor.execute(query)
        publishers_name = cursor.fetchall()
        print(publishers_name[0])

        for name in publishers_name:
            if name[1] == publishername:
                break
            publisherID=publisherID+1

        print(publisherID)
        global id
        query = "SELECT * FROM BOOK ORDER BY ID "
        cursor.execute(query)
        books = cursor.fetchall()
        for book in books:
            if book[0] > id:
                id = book[0]

        id = id + 1


        if name[1] != publishername:
            query = "INSERT INTO PUBLISHER VALUES(%d, '%s', '%s','%s')" % (publisherID,'name','phone_num','address')
            cursor.execute(query)

            query = "INSERT INTO SELLER VALUES('%s', '%s', '%s','%s')" % (isbn,"name","price","type")
            cursor.execute(query)
            query = "INSERT INTO BOOK VALUES(%d, '%s', '%s','%s',%d)" % (id,title,isbn,edition,publisherID)
            cursor.execute(query)
            publisherID=publisherID-1

            connection.commit()
            return redirect(url_for('publisher_add_page'))

        query = "INSERT INTO SELLER VALUES('%s', '%s', '%s','%s')" % (isbn,"name","price","type")
        cursor.execute(query)
        query = "INSERT INTO BOOK VALUES(%d, '%s', '%s','%s',%d)" % (id,title,isbn,edition,publisherID)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('book_page',  id=id))

@app.route('/publisher/<int:publisherID>')
def publisher_page(publisherID):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    query = "SELECT * FROM PUBLISHER ORDER BY PUB_ID"
    cursor.execute(query)

    publishers = cursor.fetchall()
    for publisher in publishers:
        if publisher[0] == publisherID:
                return render_template('publisher.html', publisher = publisher)
@app.route('/publishers/add', methods=['GET', 'POST'])
def publisher_add_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    if request.method == 'GET':
        form = {'name','phone_number', 'address'}
        connection.commit()
        return render_template('publisher_edit.html',form=form)
    else:
        name = request.form['name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        global publisherID

        publisherID=publisherID+1

        query = "UPDATE PUBLISHER SET name= '%s', phone_number='%s',address='%s' WHERE pub_id='%d'" % (name, phone_number, address,publisherID)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('publisher_page',  publisherID=publisherID))

@app.route('/book/<int:id>/edit', methods=['GET', 'POST'])
def book_edit_page(id):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    if request.method == 'GET':
        form = {'title','publishername', 'isbn','edition'}
        connection.commit()
        return render_template('book_edit.html',form=form,is_add=0)
    else:
        title = request.form['title']
        isbn = request.form['isbn']
        edition = request.form['edition']

        query = "INSERT INTO SELLER VALUES('%s', '%s', '%s','%s')" % (isbn,"name","price","type")
        cursor.execute(query)

        query = "UPDATE BOOK SET title= '%s', isbn='%s',edition='%s' WHERE id='%d'" % (title, isbn, edition, id)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('book_page', id=id))



@app.route('/sellers', methods=['GET', 'POST'])
def sellers_page():
    if request.method == 'GET':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = "SELECT * FROM SELLER JOIN BOOK ON SELLER.S_ISBN=BOOK.ISBN ORDER BY S_ISBN"
            cursor.execute(query)

            connection.commit()
        return render_template('sellers.html', sellers = cursor.fetchall())
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            deletes = request.form.getlist('sellers_to_delete')
            for delete in deletes:
                query = "DELETE FROM SELLER  WHERE S_ISBN='%s'" %delete
                cursor.execute(query)
            query = "SELECT * FROM SELLER ORDER BY S_ISBN"
            cursor.execute(query)
            connection.commit()
        return render_template('sellers.html', sellers = cursor.fetchall())



@app.route('/seller/<s_isbn>')
def seller_page(s_isbn):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

    query = "SELECT * FROM SELLER ORDER BY S_ISBN"
    cursor.execute(query)
    sellers = cursor.fetchall()
    for seller in sellers:
        if seller[0] == s_isbn:
                return render_template('seller.html', seller = seller)


@app.route('/sellers/add', methods=['GET', 'POST'])
def seller_add_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    if request.method == 'GET':
        form = {'s_isbn','name','price', 'type'}
        connection.commit()
        return render_template('seller_edit.html',form=form)
    else:
        s_isbn = request.form['s_isbn']
        name = request.form['name']
        price = request.form['price']
        type = request.form['type']

        query = "INSERT INTO SELLER VALUES ('%s','%s','%s','%s')" % (s_isbn,name, price, type)
        cursor.execute(query)
        connection.commit()
        return redirect(url_for('seller_page',  s_isbn=s_isbn))

@app.route('/seller/<s_isbn>/edit', methods=['GET', 'POST'])
def seller_edit_page(s_isbn):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()


    if request.method == 'GET':
        form = {'name','price', 'type'}
        connection.commit()
        return render_template('seller_edit.html',form=form)
    else:
        name = request.form['name']
        price = request.form['price']
        type = request.form['type']

        query = "UPDATE SELLER SET name= '%s', price='%s',type ='%s' WHERE s_isbn='%s'" % (name, price, type, s_isbn)
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('seller_page', s_isbn=s_isbn))
#######library#######


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
            query = "SELECT * FROM CATEGORIES WHERE CKEY ='%d'" %writer[3]
            cursor.execute(query)
            category = cursor.fetchall()
            return render_template('writer.html', writer = writer, awards = awards, category=category[0])

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
