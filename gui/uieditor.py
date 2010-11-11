import time

import gtk
import sqlalchemy

from gui.mapper import interface_auto_map,adapters
from gui.mapper.adapters import gtkAdapters
import clubBD.database as database

from misc import show_message

class UIEditor(object):
    def __init__(self,xml_file,fields,default):
        builder = gtk.Builder()
        builder.add_from_file(xml_file)

        self._window = builder.get_object('dialog')
        self._default = default

        builder.connect_signals(self)

        props_mapper_dict = dict((name,builder.get_object(name)) 
                                 for name in fields)

        assert(all(props_mapper_dict.itervalues()))

        self._mapper = interface_auto_map(props_mapper_dict)

        self._button_ok = builder.get_object('button_ok')
        self._button_delete = builder.get_object('button_delete')
      
        self._builder = builder

    def run(self):
        if not isinstance(self._default,type):
            self._button_ok.set_label('gtk-save')
            self._mapper.dump(self._default)
        else:
            self._default = self._default(**self._mapper.load_dict())
            self._button_ok.set_label('gtk-add')

            if self._button_delete:
                self._button_delete.set_sensitive(False)

        self._window.show_all()

        while True:
            responseid = self._window.run()
            if responseid == 0:
                resp = (None,None)
                break
            elif responseid == 1 and self.save():
                resp = ('save',self._default)
                break
            elif responseid == 2:
                self.delete()
                resp = ('delete',self._default)
                break

        self._window.destroy()
        return resp
     
    def save(self):
        self._mapper.load(self._default)
            
        try:
            with database.session.begin():
                self._default = database.session.merge(self._default)
                
            return True
            
        except sqlalchemy.exc.IntegrityError,e:
            print e
            show_message("Duplication dans la base, cet element semble deja exister",self._window)
            return False

    def delete(self):
        with database.session.begin():
            database.session.delete(self._default)

