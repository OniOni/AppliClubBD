from sqlalchemy import MetaData,create_engine,Table,or_,and_,null
from sqlalchemy.orm import mapper,relation,create_session,backref
import model


def new_session(path):
    lazy = False
    engine = create_engine('sqlite:///%s'%path,
                           convert_unicode=True
                           )
    metadata = MetaData(engine,reflect=True)

    
    table_author = Table('author',metadata,autoload=True)
    table_book = Table('book',metadata,autoload=True)
    table_editor = Table('editor',metadata,autoload=True)
    table_serial = Table('serial',metadata,autoload=True)
    table_user = Table('user',metadata,autoload=True)
    
    # for join
    table_author_to_book = Table('author_to_book',metadata,autoload=True)
        
    # mapping
    mapper(model.Serial, table_serial,
           order_by=table_serial.c.title)
    mapper(model.Author, table_author,
           order_by=table_author.c.name)
    mapper(model.Editor, table_editor,
           order_by=table_editor.c.name)
    mapper(model.User, table_user,
           order_by=table_user.c.id,
           properties={
            'books':relation(model.Book,lazy=lazy,backref='user')
            })
    mapper(model.Book,table_book,
           order_by=table_book.c.serial_id,
           properties={
            'authors':relation(model.Author,secondary=table_author_to_book,lazy=lazy),
            'editor':relation(model.Editor,lazy=lazy),
            'serial':relation(model.Serial,lazy=lazy,backref=backref('books',lazy=lazy)),
            },
           )

    return create_session(bind=engine)

def start(path):
    global session
    session = new_session(path)

__all__ = 'start','session'

if __name__ == '__main__':
    session = new_session('../db.db')

