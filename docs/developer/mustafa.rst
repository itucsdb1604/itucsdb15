Parts Implemented by Mustafa Furkan Süve
========================================

When the first time the website released, we need to initialize our database which is creating the tables and insert the initial values into them. To do this, we need to call initialize_database function. After creating the other tables, this function calls initMustafaTables function to create my tables.

Tables that I created:
----------------------
* Announcements
* Messages
* MessageLists
* Notification
* Follow

Initializing
------------
First we drop and re-create the announcements table then insert the announcements with the code given below;

.. code-block:: python

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
	
After that, we create the message lists table;

.. code-block:: python

	query = """DROP TABLE IF EXISTS MESSAGE_LISTS CASCADE"""
    cursor.execute(query)
    
	query = """CREATE TABLE MESSAGE_LISTS (
			USER_ID INT,
			NAME VARCHAR(120),
			ID SERIAL PRIMARY KEY,
			FOREIGN KEY (USER_ID) REFERENCES USERS (ID) ON DELETE CASCADE
	)"""
	cursor.execute(query)
	
This table has a foreign key referencing to the users table on id attribute. This key holds which user is that message list assign to. When a user is deleted, all of his message lists will be deleted as well.

.. code-block:: python

    query = """DROP TABLE IF EXISTS MESSAGES"""
    cursor.execute(query)
    
    query = """CREATE TABLE MESSAGES (
        LIST_ID INT,
        TEXT VARCHAR(120),
        ID SERIAL PRIMARY KEY,
        FOREIGN KEY (LIST_ID) REFERENCES MESSAGE_LISTS (ID) ON DELETE CASCADE
    )"""
    cursor.execute(query)

Then we create the message table whic has a foreign key list_id referencing to the message list table on id attribute. This key holds the id of the message list of that message. When a message list is deleted, all of the message in it will be deleted as well.

.. code-block:: python
            
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
After that, we create the follow table which holds the id of the followed user and the follower. Primary key is both the ids combined since a user can not follow someone twice. Follower_id and followed_id is the foreign keys of this table referencing users table on id attribute. Moreover, when a user is deleted, all of the “follow” informations of him is deleted as well.

.. code-block:: python

	query = """DROP TABLE IF EXISTS NOTIFICATION"""
    cursor.execute(query)
    
    query = """CREATE TABLE NOTIFICATION (
    	USER_ID INT,
        TEXT VARCHAR(120),
        ID SERIAL PRIMARY KEY,
        FOREIGN KEY (USER_ID) REFERENCES USERS (ID) ON DELETE CASCADE
    )"""
    cursor.execute(query)
    
Finally we create the notification table which holds the notifications of the users. This table has a foreign key which is user_id referencing the users table on id attribute. Furthermore, when a user is deleted, all of his notifications will be deleted as well.

Follow
------
When the follow page is called, we first select all the users to show them to the user. Then we take the ones that the user already followed to make sure that he can not follow anyone twice.

.. code-block:: python

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

If the user wants to follow someone we get all the ids of the users to follow then insert them into the follow table. Finally we send a notification to the followed user.

.. code-block:: python

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

Unfollow
--------
User can unfollow the users that he followed. The query that is used to do this is below;

.. code-block:: python

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

Notification Delete
-------------------
When a user wants to delete his notifications, this code will run.

.. code-block:: python

    query = """DELETE FROM NOTIFICATION
                    WHERE(ID = %s)
            """ % id
    cursor.execute(query)

Getting Notifications
---------------------
Whenever a user is followed or unfollowed by another user, the followed one gets a notidication.
Furthermore, if the followed user does an operation regarding messages and message lists,
the follower will get a notification about that operation.

.. code-block:: python

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

This is the code that notificate the users. In this process we first
get the userID and the userName. Then by using the userID, we get all
the users that is following the user having that userID. Then we get
the list name for the content of the notification. Finally we give
notification to all users that follows him.

This process is repeated in all the functions related to messages,
message lists, follow and unfollow.

Message Board
-------------
To select the messages and put it on the website we used this query;

.. code-block:: python


