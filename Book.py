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
    