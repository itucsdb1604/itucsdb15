class ReadBook:
    photo_url = ""
    def __init__(self, id, bookName, authorName, publishYear, readYear = 2000, description = "Description"):
        self.id = id;
        self.bookName = bookName
        self.authorName = authorName
        self.publishYear = publishYear
        self.readYear = readYear
        self.description = description
        
    
    def __iter__(self):
        return iter(self.bookName,
                self.authorName,
                self.publishYear,
                self.readYear,
                self.description)
    