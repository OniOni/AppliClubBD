"""
Adapter for part of gtk widgets

You usually just want to import that module and use mapper.interface_auto_map.
"""

import pygtk
pygtk.require('2.0')
import gtk
import datetime

from gui.mapper.adapters import Adapter

def to_unicode(f):
    def _(self):
        return unicode(f(self))
    return _


class gtkEntryAdapter(Adapter):
    _class = gtk.Entry
    
    @to_unicode
    def get(self):
        return self._widget.get_text()

    def set(self,value):
        if value:
            self._widget.set_text(value)
        else:
            self._widget.set_text('')

class gtkCheckButton(Adapter):
    _class = gtk.CheckButton

    def get(self):
        return self._widget.get_active()

    def set(self,value):
        self._widget.set_active(value)


class gtkSpinButtonAdapter(Adapter):
    _class = gtk.SpinButton

    def get(self):
        val = self._widget.get_value()
        if int(val) == float(val):
            return int(val)

    def set(self,value):
        self._widget.set_value(value)

class gtkComboBox(Adapter):
    _class = gtk.ComboBox

    def get(self):
        model = self._widget.get_model()
        iter = self._widget.get_active_iter()

        return model.get_value(iter,0) if iter else None

    def set(self,value):
        if value:
            model = self._widget.get_model()
            
            for index,row in enumerate(model):
                if row[0] == value:
                    self._widget.set_active(index)
                    break
            else:
                raise ValueError("Object %r does not exists in this model"%obj)

class gtkCalendar(Adapter):
    _class = gtk.Calendar
    def get(self):
        year,month,day = self._widget.get_date()
        month += 1 # du to 0 based month
        return datetime.date(year,month,day)

    def set(self,date):
        if date:
            self._widget.select_month(date.month - 1,date.year)
            self._widget.select_day(date.day)

class gtkTreeView(Adapter):
    _class = gtk.TreeView
    
    def get(self):
        selection = self._widget.get_selection()
        if selection.get_mode() != gtk.SELECTION_MULTIPLE:
            model, iter = selection.get_selected()
            return model.get_value(iter,0) if iter else None
        else:
            l = []
            model, paths = selection.get_selected_rows()
            for path in paths:
                iter = model.get_iter(path)
                l.append(model.get_value(iter,0))

            return l
            
    def set(self,values):
        selection = self._widget.get_selection()
        model = self._widget.get_model()

        if values:
            values = values[:] if selection.get_mode() == gtk.SELECTION_MULTIPLE else [values]
                
            for index,row in enumerate(model):
                if row[0] in values:
                    self._widget.get_selection().select_path(index)
                    values.remove(row[0])
                        
                    if not values:
                        break
            else:
                raise ValueError("Object %r does not exists in this model"%values)


class RadioButtonMapper(object):
    def __init__(self,dict): # wait for a dict {value:widget}
        self.dict = dict

    def get(self):
        for value,widget in self.dict.iteritems():
            if widget.get_active():
                return value

    def set(self,value):
        self.dict[value].set_active(True)
