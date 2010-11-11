import os.path
import gtk
from generic_tree import Model, Column, TreeviewProxy

class ChooseModel(object):
    def __init__(self,model,have=tuple()):
        self._have = set(have)

        self.filter_have = fh = model.filter_new()
        self.filter_available = fa = model.filter_new()

        fh.filter_func = lambda obj: obj not in self._have
        fa.filter_func = lambda obj: obj in self._have

    def remove(self,value):
        self._have.remove(value)
        self.refilter()

    def add(self,value):
        self._have.add(value)
        self.refilter()

    def refilter(self):
        self.filter_available.refilter()
        self.filter_have.refilter()

    def pack(self,have,available):
        self.filter_have.affect(have)
        self.filter_available.affect(available)

class ChooseModelAdapter(object):
    def __init__(self,model):
        self._model = model

    def get(self):
        # TODO: a bit hackish
        return list(self._model._have)

    def set(self,values):
        self._model._have.clear()
        self._model._have.update(values)
        self._model.refilter()

class ChooseWidget(object):
    def __init__(self, model, columns, trees, filter):
        have, available = trees
        col_have, col_available = columns

        have.connect('row-activated',self._update,model.remove)
        available.connect('row-activated',self._update,model.add)

        TreeviewProxy(have).set_search_func(filter)
        TreeviewProxy(available).set_search_func(filter)

        model.pack(available,have)

        col_have.pack(have)
        col_available.pack(available)

    def _update(self, tree, path, column, method):
        row = TreeviewProxy(tree).get_selected_row()
        
        if row:
            method(row())

if __name__ == '__main__':
    import string

    model = Model()
    model.load(open(__file__).read().split())

    model = ChooseModel(model,'y x z'.split())

    have, available = gtk.TreeView(), gtk.TreeView()
    vp_have, vp_available = gtk.ScrolledWindow(), gtk.ScrolledWindow()

    def filter(obj, key):
        return key.lower() in obj.lower()

    sel = ChooseWidget(model,
                       (Column("Have",str),Column('Nohave',str)),
                       (have, available),
                       filter)

    w = gtk.Window()
    box = gtk.HBox()
    
    vp_have.add(have)
    vp_available.add(available)

    box.add(vp_have)
    box.add(vp_available)

    w.add(box)

    w.show_all()
    gtk.main()
