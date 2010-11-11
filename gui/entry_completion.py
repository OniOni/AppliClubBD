import gtk

class EntryCompletion(object):
    def __init__(self, entry, model, display_func, match_func):
        self._entry = entry
        self._display_func = display_func
        self._match_func = match_func
        self._model = model._model

        self._obj = None

        completion = gtk.EntryCompletion()
        entry.set_completion(completion)

        cell = gtk.CellRendererText()
        completion.pack_start(cell)
        completion.set_cell_data_func(cell,self._display)

        completion.set_model(model._model)
        completion.set_inline_selection(True)
        completion.set_inline_completion(True)
        completion.set_match_func(self._match)

        completion.connect('match-selected',self._mselected)
        entry.connect('changed',self._changed)

    def _display(self,column,cell,model,iter):
        obj = model.get_value(iter,0)
        cell.set_property('text',self._display_func(obj))

    def _match(self,completion, key, iter):
        obj = completion.get_model().get_value(iter, 0)

        return self._match_func(obj, key)

        text = model.get_value(iter, 0).name

        if text.lower().startswith(key.lower()):
            return True
        return False

    def _mselected(self, completion, model, iter):
        obj = model.get_value(iter, 0)
        completion.get_entry().set_text(self._display_func(obj))

        return True

    def _changed(self, entry):
        text = entry.get_text()
        
        if self._find_obj(text):
            entry.set_icon_from_stock(gtk.ENTRY_ICON_PRIMARY,'gtk-yes')
        else:
            entry.set_icon_from_stock(gtk.ENTRY_ICON_PRIMARY,'gtk-no')

    def _find_obj(self,text):
        for obj in self._model:
            if self._display_func(obj[0]) == text:
                return obj[0]

    def get(self):
        return self._find_obj(self._entry.get_text())

    def set(self,value):
        if value:
            self._entry.set_text(self._display_func(value))

if __name__ == '__main__':
    import generic_tree

    import sys
    sys.path.insert(0,'..')

    import clubBD.database
    import clubBD.model

    clubBD.database.start('../db.db')

    model1 = generic_tree.Model(clubBD.database.session.query(clubBD.model.Editor))
    model2 = generic_tree.Model(clubBD.database.session.query(clubBD.model.Serial))

    w = gtk.Window()
    b = gtk.VBox()

    e1 = gtk.Entry()
    e2 = gtk.Entry()

    b.add(e1)
    b.add(e2)

    w.add(b)

    def match_func_name(obj, key):
        return obj.name.lower().startswith(key.lower())

    def match_func_title(obj, key):
        return obj.title.lower().startswith(key.lower())

    def display_func_name(obj):
        return obj.name

    def display_func_title(obj):
        return obj.title

    EntryCompletion(e1, model1, display_func_name, match_func_name)
    EntryCompletion(e2, model2, display_func_title, match_func_title)
    
    w.show_all()
    gtk.main()
