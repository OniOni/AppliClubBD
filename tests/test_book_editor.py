from bookeditor import BookEditor
import clubBD.database as database

import pygtk
pygtk.require('2.0')

import gtk
import sys

database.start('db.db')

if sys.argv[1:]:
    id = sys.argv[1]
    obj = database.session.query(database.model.Book).get(id)
else:
    obj = database.model.Book

ui = BookEditor('ui/dialog_book.xml',['title','ean','reference','buy_date','serial_nb'],obj)
ret = ui.run()

print ret, ret.id

#gtk.main()
