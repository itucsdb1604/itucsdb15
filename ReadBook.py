class ReadBook:
    def __init__(self, id, bookName, authorName, publishYear, readYear):
        self.id = id;
        self.bookName = bookName
        self.authorName = authorName
        self.publishYear = publishYear
        self.readYear = readYear
    
    def __iter__(self):
        return iter(self.bookName,
                self.authorName,
                self.publishYear,
                self.readYear)
    