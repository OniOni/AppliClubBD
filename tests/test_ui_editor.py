from uieditor import UIEditor
import clubBD.database as database

import pygtk
pygtk.require('2.0')

import gtk
import sys

database.start('db.db')

if sys.argv[1:]:
    id = sys.argv[1]
    obj = database.session.query(database.model.Editor).get(id)
else:
    obj = database.model.Editor

ui = UIEditor('ui/dialog_editor.xml',['name'],obj)
ret = ui.run()

print ret, ret.id

#gtk.main()
