import datetime
import itertools

class Book(object):
    def __init__(self,title,ean,reference,editor=None,authors=None,serial=None,serial_nb=None,buy_date=None,kind=None):
        self.title = title
        self.ean = ean
        self.reference = reference

        self.editor = editor
        self.authors = authors

        self.buy_date = buy_date

        self.serial = serial
        self.serial_nb = serial_nb

        self.kind = kind

        self.emprunt = None
        self.date_start = None

    def __repr__(self):
        return "Book(%(title)r,%(editor)r,%(authors)r,%(buy_date)r,%(reference)s,%(kind)s)" % vars(self)

    def __str__(self):
        return "%(title)s %(reference)s" % vars(self)

    def loan_length(self):
        if self.user_id:
            return (datetime.date.today() - self.date_start).days
        else:
            return None
            
class Editor(object):
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return "Editor(%(name)r)" % vars(self)

    def __str__(self):
        return str(self.name)

class Author(object):
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return "Author(%(name)r)" % vars(self)

    def __str__(self):
        return self.name

class Serial(object):
    def __init__(self,title):
        self.title = title

    def __repr__(self):
        return repr(self.title)

    def get_prefix(self):
        return set(book.reference[:5] for book in self.books)
    
    prefix = property(get_prefix)

class User(object):
    def __init__(self,firstname,lastname,mail,phone,address,nb_items,student_number,year):
        self.firstname = firstname
        self.lastname = lastname
        self.student_number = student_number
        self.mail = mail
        self.phone = phone
        self.address = address
        self.items = nb_items
    
        self.books = []
        self.year = year

    def __repr__(self):
        return "User(%(firstname)r,%(lastname)r,%(student_number)r,%(mail)r,%(phone)r,%(address)r,%(nb_bd)r,%(nb_mangas)r)" % vars(self)
    
    def __str__(self):
        return "%(firstname)s %(lastname)s" % vars(self)

    def get_mangas_nb(self):
        return len([i for i in self.books if i.kind == 'm'])

    def get_bd_nb(self):
        return len([i for i in self.books if i.kind == 'b'])

    def is_full_manga(self):
        return self.get_mangas_nb() == self.nb_mangas
         
    def is_full_bd(self):
        return self.get_bd_nb() == self.nb_bd

    def get_manga_ratio(self):
        return self.get_mangas_nb(),self.nb_mangas

    def get_bd_ratio(self):
        return self.get_bd_nb(),self.nb_bd

    def returns(self,book):
        book.date_start = None
        self.books.remove(book)

    def takes(self,book):
        book.date_start = datetime.date.today()
        self.books.append(book)
