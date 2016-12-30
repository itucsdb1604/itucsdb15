Parts Implemented by Tolga Şen
==============================

When the profile page or library page is being clicked, it routes to the handler functions in the server.py file as seen below.

Profile Page
------------

**Profile Page Router Function:**

.. code-block:: python

   @app.route('/profile', methods=['GET', 'POST'])
   def profile_page():
       bookList = handleReadList(request)
       readBooks = getBooksFromReadList()
       return render_template('profile.html', readbooks = readBooks, booklist = bookList, size = len(readBooks))

**The ReadBook class for modeling the books which user has read**

.. code-block:: python

   class ReadBook:
       photo_url = ""
       def __init__(self, id, bookName, authorName, publishYear, readYear = 2000, description = "Description"):
           self.id = id;
           self.bookName = bookName
           self.authorName = authorName
           self.publishYear = publishYear
           self.readYear = readYear
           self.description = description

.. code-block:: python

   def __iter__(self):
           return iter(self.bookName,
                   self.authorName,
                   self.publishYear,
                   self.readYear,
                   self.description)

**Profile Page Handler Function**
After clicking the profile page, it starts to handle the click events, table initialization:

.. code-block:: python

   def handleReadList(request):
       create_readList()

       if('saveButton' in request.form):
           if request.method == 'GET':
               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """
                           SELECT * FROM read_list;
                       """
                   cursor.execute(query)
                   connection.commit()
           else:
               bookName = request.form['bookName']
               readYear = request.form['readYear']

               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """
                           SELECT id FROM book_list
                               WHERE(title = '""" + bookName + """');
                       """
                   cursor.execute(query)
                   connection.commit()
                   id = 0
                   for row in cursor.fetchall():
                       id = row[0]

                   newID = newIDFromReadList()
                   query = """
                           INSERT INTO read_list(id, read_year, book_id)
                           VALUES("""+ str(newID) + "," + str(readYear) + "," + str(id) + """);"""

                   cursor.execute(query)
                   connection.commit()

       elif('delete' in request.form):
           with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               booksToDelete = request.form.getlist('booksToDelete')
               for id in booksToDelete:
                   deleteBookFromReadList(id)
                   print("ID:" + str(id))

       return getBooksFromLibrary()

**Creating the read_list table:**

.. code-block:: python

   def create_readList():
       with dbapi2.connect(app.config['dsn']) as connection:
           cursor = connection.cursor()
           #Creating the readlist table
           query = """
                       CREATE TABLE IF NOT EXISTS read_list(
                           id int,
                           read_year NUMERIC(4),
                           book_id int,
                           PRIMARY KEY (id)
                           );
                   """
           cursor.execute(query)
           connection.commit()
       return render_template('profile.html')

**Deleting a book from readlist:**

.. code-block:: python

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

**Updating a book in the read list:**

.. code-block:: python

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

Library Page:
-------------

**Library Page Router Function:**

.. code-block:: python

   @app.route('/library', methods=['GET', 'POST'])
   def library_page():
       libraryBooks = handleBookList(request)
       return render_template('library.html', books = libraryBooks, size = len(libraryBooks))

**The Book.py class for modeling the books which exists in the library**
In this part, there is a default photo url of a book. On following parts, when the book is being added into library, and its name matches one with the pre-defined photo url's for some specific books, this default url will be replaced with the new one.

.. code-block:: python

   class Book:
       photo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png"

       def __init__(self, id, title, author, publishYear, description, publisher, isbn, edition):
           self.id = id
           self.title = title
           self.author = author
           self.publishYear = publishYear
           self.description = description
           self.publisher = publisher
           self.isbn = isbn
           self.edition = edition

       def __iter__(self):
           return iter(self.id,
                   self.title,
                   self.author,
                   self.publishYear,
                   self.description,
                   self.publisher,
                   self.isbn,
                   self.edition)

**Library page handler function:**

.. code-block:: python

   def handleBookList(request):
       create_bookList()
       if('save' in request.form):
           if request.method == 'POST':
               title = request.form['title']
               author = request.form['author']
               publishYear = request.form['publishYear']
               description = request.form['description']
               publisherName = request.form['publisherName']
               isbn = request.form['isbn']
               edition = request.form['edition']

               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()

                   newID = newIDFromBookList()
                   query = """
                           INSERT INTO book_list(id, title, author, publish_year, description,
                           publisher_name, isbn, edition)
                           VALUES(%s, '%s', '%s', %s, '%s', '%s', %s, %s)""" % (newID, title, author, publishYear, description, publisherName,isbn, edition)
                   cursor.execute(query)
                   connection.commit()

       return getBooksFromLibrary()

**Creating the book_list table:**

.. code-block:: python

   def create_bookList():
       with dbapi2.connect(app.config['dsn']) as connection:
           cursor = connection.cursor()
           #Creating the book_list table
           query = """
                       CREATE TABLE IF NOT EXISTS book_list(
                           id int,
                           title varchar(60),
                           author varchar(40),
                           publish_year NUMERIC(4),
                           description varchar(200),
                           publisher_name varchar(40),
                           isbn varchar(20),
                           edition int,
                           PRIMARY KEY (id)
                           );
                   """
           cursor.execute(query)
           connection.commit()
       return render_template('profile.html')

**Getting existing books from library**

.. code-block:: python

   def getBooksFromLibrary():
       with dbapi2.connect(app.config['dsn']) as connection:
           books = list()
           cursor = connection.cursor()
           query = """
                   SELECT * FROM book_list;
               """
           cursor.execute(query)
           for row in cursor.fetchall():
               id, title, author, publishYear, description, publisher, isbn, edition = row
               books.insert(len(books), Book(id, title, author, publishYear, description, publisher, isbn, edition))

           for book in books:
               if book.title == 'Hobbit':
                   book.photo_url = "https://cdn.pastemagazine.com/www/system/images/photo_albums/hobbit-book-covers/large/photo_5653_0-7.jpg?1384968217"
               elif book.title == 'Tutunamayanlar':
                   book.photo_url = "http://yazarokur.com/rsm/kitap/_ko/tutunamayanlar.jpg"
               elif book.title == "Korkuyu Beklerken":
                   book.photo_url = "http://www.iletisim.com.tr/images/UserFiles/images/Spot/120402153824.jpg"
               elif book.title == 'Dijital Kale':
                   book.photo_url = "https://upload.wikimedia.org/wikipedia/tr/thumb/6/61/Dijital_Kale.jpg/220px-Dijital_Kale.jpg"
               elif book.title == 'Denemeler':
                   book.photo_url = "http://www.birazoku.com/wp-content/uploads/2013/01/denemeler-michel-de-montaigne.jpg"

           return books

