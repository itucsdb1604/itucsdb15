Parts Implemented by Sergen KAYIKCI
================================

	First drop the awards, writers and categories tables, then create them again and them initialize them with
some examples. Primary key of categories table is foreign key of writers table and primary key of writers table
is foreign key of awards table.

.. code-block:: python

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
        
        
add operation for writers.

.. code-block:: python

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
        
delete operation for writers.

.. code-block:: python

        deletes = request.form.getlist('writers_to_delete')
        for delete in deletes:

            query = "DELETE FROM WRITERS WHERE KEY='%s'" %delete
            cursor.execute(query)
            
edit operation for writers.

.. code-block:: python

        name = request.form['name']
        age = request.form['age']
        categoryid = int(request.form['categoryid'])

        query = "UPDATE WRITERS SET name= '%s', age='%s',categoryid ='%d' WHERE KEY='%d'" % (name, age, categoryid, key)
        cursor.execute(query)

add operation for categories.

.. code-block:: python

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
        
delete operation for categories.

.. code-block:: python

        deletes = request.form.getlist('categories_to_delete')
        for delete in deletes:

            query = "DELETE FROM CATEGORIES WHERE CKEY='%s'" %delete
            cursor.execute(query)
            
edit operation for categories.

.. code-block:: python

        name = request.form['name']
        feature = request.form['feature']

        query = "UPDATE CATEGORIES SET name= '%s', feature='%s' WHERE CKEY='%d'" % (name, feature, ckey)
        cursor.execute(query)

add operation for awards.

.. code-block:: python

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
        
delete operation for awards.

.. code-block:: python

        deletes = request.form.getlist('awards_to_delete')
        for delete in deletes:
            query = "DELETE FROM AWARDS WHERE AKEY='%s'" %delete
            cursor.execute(query)
            
edit operation for awards.

.. code-block:: python

        name = request.form['name']
        year = request.form['year']
        writerid = int(request.form['writerid'])

        query = "UPDATE AWARDS SET name= '%s', year='%s',writerid ='%d' WHERE AKEY='%d'" % (name, year, writerid, akey)
        cursor.execute(query) 
        
