import operator
import time

import pygtk; pygtk.require('2.0')

import gtk
import gobject

class TreeviewRowProxy(object):
    def __init__(self, obj, path, iter, model):
        self.obj = obj
        self._path = path
        self._iter = iter
        self._model = model

    def changed(self):
        self._model.row_changed(self._path,self._iter)

    def remove(self):
        model, iter = self._model, self._iter
        while hasattr(model,'get_model'):
            model, iter = model.get_model(), model.convert_iter_to_child_iter(iter)

        model.remove(iter)

    def __call__(self):
        return self.obj

class TreeviewProxy(object):
    def __init__(self,treeview):
        self._treeview = treeview

    def optimise_tree(self, size):
        for col in self._treeview.get_columns():
            col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            col.set_fixed_width(size)
            col.set_resizable(True)

        self._treeview.set_fixed_height_mode(True)

    @classmethod
    def by_selection(cls,selection):
        return cls(selection.get_tree_view())
    
    def get_row(self,path=None,iter=None):
        model = self._treeview.get_model()
        if iter:
            path = model.get_path(iter)
        elif path:
            iter = model.get_iter(path)

        obj = model.get_value(iter,0)

        return TreeviewRowProxy(obj,path,iter,model)

    def get_selected_row(self):
        model, iter = self._treeview.get_selection().get_selected()

        return self.get_row(iter=iter) if iter else None

    @classmethod
    def quick(cls,treeview,columns,model):
        tree = cls(treeview)
        tree.extend_columns(columns)
        model.affect(treeview)

    def append_column(self, column):
        self._treeview.append_column(column._column)

    def extend_columns(self, columns):
        for col in columns:
            self.append_column(col)

    def set_search_func(self, func):
        self._treeview.set_enable_search(True)
        self._treeview.set_search_column(0)
        self._treeview.set_search_equal_func(self._search_func,func)

    def _search_func(self, model, column, key, iter, func):
        obj = model.get_value(iter,0)
        return not func(obj,key)

class Model(object):
    def __init__(self,items=None):
        self._model = gtk.ListStore(object)

        if items:
            self.load(items)
        
    def load(self,items):
        for item in items:
            self.append(item)

    def affect(self,tree):
        tree.set_model(self._model)

    def filter_new(self):
        return ModelFilter(self._model)

    def append(self,obj):
        self._model.append([obj])

class ModelFilter(Model):
    def __init__(self,model):
        self._parent = model

        self._model = model.filter_new()
        self._model.set_visible_func(self._filter)

        # set the default func that filter everything
        self.filter_func = self.all

    def _filter(self,model,iter):
        obj = model.get_value(iter,0)
        # TODO... I dislike that stuff
        return obj and self.filter_func(obj)

    def all(self,obj):
        return True

    def refilter(self):
        self._model.refilter()

    def load(self,items):
        raise NotImplementedError

class Column(object):
    _props = "foreground".split()

    def __init__(self,title,display):
        cell = gtk.CellRendererText()
        self._column = gtk.TreeViewColumn(title,cell)

        # display stuff
        func = display if callable(display) else operator.attrgetter(display)
        self._column.set_cell_data_func(cell,self._wrap,func)

    def _wrap(self,column,cell,model,iter,func):
        obj = model.get_value(iter,0)

        for prop in self._props:
            cell.set_property(prop,None)


        ret = func(obj)
        if isinstance(ret,dict):
            for key, value in ret.iteritems():
                cell.set_property(key,value)
        else:
            cell.set_property('text',ret)

            
    def pack(self,tree):
        tree.append_column(self._column)


class ComboxBoxProxy(object):
    def __init__(self,combox,display,model):
        cell = gtk.CellRendererText()
        self._column = combox
        combox.pack_start(cell)

        # display stuff
        func = display if callable(display) else operator.attrgetter(display)
        self._column.set_cell_data_func(cell,self._wrap,func)

        combox.set_model(model._model)

    def _wrap(self,column,cell,model,iter,func):
        obj = model.get_value(iter,0)
        cell.set_property('text',func(obj))

    def get_object(self):
        model = self._column.get_model()
        iter = self._column.get_active_iter()

        return model.get_value(iter,0) if iter else None

    def set_object(self,obj):
        model = self._column.get_model()
        
        for index,row in enumerate(model):
            if row[0] == obj:
                self._column.set_active(index)
                break
        else:
            raise ValueError("Object %r does not exists in this model"%obj)




if __name__ == '__main__':
    class Object(object):
        def __init__(self,name):
            self.name = name

    win = gtk.Window()
    tree = gtk.TreeView()
    filtered_tree = gtk.TreeView()

    box = gtk.HBox()
    box.add(tree)

    vbox = gtk.VBox()
    vbox.add(box)


    combo = gtk.ComboBox()
    vbox.pack_start(combo,expand=False)
    
    win.add(vbox)

    box.add(filtered_tree)

    store = Model()
    store_filtered = store.filter_new()

    col = Column('Object ID','name')
    col.pack(tree)

    col = Column('Object ID','name')
    col.pack(filtered_tree)

    win.show_all()
    store.load((Object(name) for name in 'hibou toto tata'.split()))
    store.affect(tree)

    store_filtered.affect(filtered_tree)

    store_filtered.filter_func = lambda obj: 't' in obj.name
    store_filtered.refilter()

    cb = ComboxBoxProxy(combo,'name',store)
    cb.set_object(store._model[1][0])
    
    def tortue():
        print "tortue",cb.get_object()
        return True

    import gobject
    gobject.timeout_add(1000,tortue)


    gtk.main()


