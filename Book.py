class Book:
    def __init__(self, id, bookName, isbn, edition):
        self.id = id
        self.bookName = bookName
        self.isbn = isbn
        self.edition = edition
    
    def __iter__(self):
        return iter(self.bookName,
                self.isbn,
                self.edition)
    