Parts Implemented by Member Name
================================

Initialize User and User Type Tables
------------------------------------

When user visit localhost:5000/initdb, then program initialize tables by using below code.

.. code-block:: python

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

User types inserted in begining because these are predefined by system. After user types are created then user table is created.

.. code-block:: python

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

Sign Up
-------

When user visit sign up page then below code works and run userlist function. If POST method is working then depend on the operation signup or delete function runs.

.. code-block:: python

   def handleSignUp():
       if request.method == 'GET':
           return userList()
       else:
           if 'signup' in request.form:
               return signUp()
           elif 'delete' in request.form:
               return deleteUser()

userList function writes user's information to the sign up page.

.. code-block:: python

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

signUp function collects information with text boxes and send them to database.

.. code-block:: python

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

deleteUser function works depend on the button it deletes user in database.

.. code-block:: python

   def deleteUser():
       with dbapi2.connect(app.config['dsn']) as connection:
           cursor = connection.cursor()

           print(request.form['delete'])

           query = "DELETE FROM USERS WHERE(ID = %s)" % request.form['delete']
           cursor.execute(query)

           connection.commit()
       return redirect(url_for('signup_page'))

In user list when user click update button then userEdit function works and update user information depend on which user is selected

.. code-block:: python

   def userEdit(userID):
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


Admin Settings
--------------

If admin is signed then admin setting page becomes active. In admin setting page userTypesList function runs and list user types. Depend on the user types update and delete functions work for that type.

.. code-block:: python

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

userTypesList function works like userList function but list user types.

.. code-block:: python

   def userTypeList():
       with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()

               query = "SELECT * FROM USERSTYPES ORDER BY ID"
               cursor.execute(query)

               connection.commit()
       return render_template('adminsettings.html', types = cursor.fetchall())

Update and delete function work for selected type and update function collect information for that type and change for database.

.. code-block:: python

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

.. code-block:: python

   def adminDelete():
       with dbapi2.connect(app.config['dsn']) as connection:
           cursor = connection.cursor()
           query = "DELETE FROM USERSTYPES WHERE(ID = 0)"
           cursor.execute(query)
           connection.commit()
       return redirect(url_for('signup_page'))

.. code-block:: python

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

.. code-block:: python

   def memberDelete():
       with dbapi2.connect(app.config['dsn']) as connection:
           cursor = connection.cursor()
           query = "DELETE FROM USERSTYPES WHERE(ID = 1)"
           cursor.execute(query)
           connection.commit()
       return redirect(url_for('signup_page'))

.. code-block:: python

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

.. code-block:: python

   def guestDelete():
       with dbapi2.connect(app.config['dsn']) as connection:
           cursor = connection.cursor()
           query = "DELETE FROM USERSTYPES WHERE(ID = 2)"
           cursor.execute(query)
           connection.commit()
       return redirect(url_for('signup_page'))
