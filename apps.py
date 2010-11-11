#coding: utf8
from __future__ import division

import time
import datetime
import os.path

from clubBD import database, model, filter
from gui.generic_tree import Model,ModelFilter,Column,TreeviewProxy

from gui import uieditor

from clubBD.bookeditor import BookEditor

import gtk
import gobject

import config

from gui.misc import show_message

class UI(object):
    def __init__(self,filename):
        self._builder = gtk.Builder()
        self._builder.add_from_file(filename)
        self._builder.connect_signals(self)

        self._w = self._builder.get_object('main')
        self._w.connect('delete-event',lambda x,y:gtk.main_quit())

        self._real_models = {}
        self._models = {}

        self._filter = None
    
    def unselect(self,trees):
        for tree in trees:
            self._builder.get_object('tree_%s'%tree).get_selection().unselect_all()
    
    def build_tree(self,name,cols):
        tree = self._builder.get_object('tree_%s'%name)
        TreeviewProxy.quick(tree,
                            cols,
                            self._models[name])

        TreeviewProxy(tree).optimise_tree(config.column_size)

    def feed(self):
        dsq = database.session.query

        builder = gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__),'ui/splash.xml'))

        win = builder.get_object('splash')
        bar = builder.get_object('progressbar')
        win.show_all()
        
        self._start_t = time.time()

        models = []

        for name in 'authors users editors serials books'.split():
            self._real_models[name] = m = Model()
            items = dsq(getattr(model,name.title()[:-1]))
            
            models.append((m,name, items,items.count()))

        nb_max = sum(i[3] for i in models)
        done = 0
        for model_index,(m,name, items, count) in enumerate(models):
            for item_index,item in enumerate(items):
                done += 1
                
                if done % config.splash_progress == 0:
                    bar.set_fraction(done / nb_max)
                    bar.set_text("Loading %s [%s of %s] [%s / %s]"%(
                            name.title(), model_index, len(models),item_index, count))
                    gtk.main_iteration(False)
                
                m._model.append([item])

        win.destroy()

        print "fill in ",time.time() - self._start_t

    def run(self):
        self.feed()
        self.build()

        for tree in 'serials authors editors'.split():
            treeview = self._builder.get_object('tree_%s'%tree)
            treeview.get_selection().connect('changed',self.on_selection_change,tree)

        # for user filtering
        treeview = self._builder.get_object('tree_users')
        treeview.get_selection().connect('changed',self.on_selection_user_change)

        self._filter = filter.FilterCollection(self._models, config.filter_timeout)
    
    def build(self):
        '''
        Create ALL models, tree and columns for the application
        '''

        self._models = dict((name, model.filter_new()) 
                            for name, model in self._real_models.iteritems())

        self._models['loans'] = self._real_models['books'].filter_new()

        def format_authors(obj):
            if len(obj.authors) > 1:
                return ', '.join(i.name for i in obj.authors)
            elif len(obj.authors) == 1:
                return obj.authors[0].name
            else:
                return ''

        def format_serial(obj):
            if obj.serial:
                return obj.serial.title
            else:
                return ''

        def format_type(obj):
            return {'m':'Manga','b':'BD'}[obj.kind]

        def format_loan(obj):
            if not obj.user_id:
                return '-'
            
            if obj.loan_length() > config.loan_length:
                return dict(text=str(obj.loan_length() - config.loan_length),
                            foreground='red')
            else:
                return dict(text=str(config.loan_length - obj.loan_length()),
                            foreground='green')

        cols = (
            Column('Reference','reference'),
            Column('Titre','title'),
            Column('Serie',format_serial),
            Column('Emprunt',format_loan),
            Column('Editeur','editor'),
            Column('Auteurs',format_authors),
            Column('Type',format_type),
        )
        self.build_tree('books',cols)

        cols = (
            Column('Editeur','name'),
        )
        self.build_tree('editors',cols)


        cols = (
            Column('Auteur','name'),
        )
        self.build_tree('authors',cols)


        def format_prefix(obj):
            if len(obj.prefix) == 1:
                return list(obj.prefix)[0]
            else:
                return dict(text=', '.join(obj.prefix),
                            foreground='red')

        cols = (
            Column('Prefix',format_prefix),
            Column('Serie','title'),
        )
        self.build_tree('serials',cols)


        def format_nb(obj):
            left = len(obj.books)
            max = obj.nb_items
            
            return dict(text='%s / %s'%(left,max),
                        foreground='green' if left < max else 'red')

        def format_mode(obj):
            return "Année" if obj.year else "Semestre"

        def format_status(obj):
            lates = [book.loan_length()
                     for book in obj.books
                     if book.loan_length() and  book.loan_length() > config.loan_length]
            if not lates:
                return "Ok"
            else:
                return dict(text="%d - %d jours"%(len(lates),sum(lates) - config.loan_length * len(lates)),
                            foreground='red')

        cols = (
            Column('Id','id'),
            Column('Prénom','firstname'),
            Column('Nom','lastname'),
            Column('Numéro','student_number'),
            Column('Mail','mail'),
            Column('Emprunts',format_nb),
            Column('Status',format_status),
            Column('Formule',format_mode)
            )

        self.build_tree('users',cols)

        def format_user(obj):
            if obj.user:
                return '%s %s'%(obj.user.firstname,obj.user.lastname)
            else:
                return "-"

        def format_uid(obj):
            return obj.user.id if obj.user else '-'

        cols = (
            Column('Reference','reference'),
            Column('Titre','title'),
            Column('Utilisateur',format_user),
            Column('Uid',format_uid),
            Column('Restant',format_loan)
            )

        self.build_tree('loans',cols)
      
    def on_selection_change(self, selection, selected_tree):
        obj = TreeviewProxy.by_selection(selection).get_selected_row()

        if obj:
            self.unselect(set(('authors','editors','serials'))-set((selected_tree,)))
            
        self._filter.refilter_obj(obj() if obj else None)

    def on_selection_user_change(self, selection):
        obj = TreeviewProxy.by_selection(selection).get_selected_row()
        self._filter.refilter_loans(obj() if obj else None)

    def clear_field(self, widget, _, event):
        widget.set_text('')
  
    def on_entry_search_changed(self,widget):
        text = widget.get_text().lower().strip()
        self._filter.refilter_value(text)
 
    def on_entry_search_books_changed(self,widget):
        text = widget.get_text().lower().strip()
        self._filter.refilter_text(text)

    def on_entry_search_user_changed(self,widget):
        text = widget.get_text().lower().strip()
        self._filter.refilter_user(text)

    def on_button_clear_selection_clicked(self, widget):
        self.unselect(set(('authors','editors','serials')))

    def on_button_clear_selection_user_clicked(self, widget):
        self.unselect(set(('users',)))

    def on_tree_loans_row_activated(self,treeview,path,view_column):
        book_p = TreeviewProxy(treeview).get_selected_row()
        user_p = TreeviewProxy(self._builder.get_object('tree_users')).get_selected_row()

        if not user_p:
            show_message('Vous devez avoir selectionné un utilisateur pour rendre des ouvrages')
        else:
            with database.session.begin():
                if book_p().user:
                    # rendu
                    assert book_p().user == user_p()
                    user_p().returns(book_p())
                else:
                    # emprunt
                    # TODO: check abo (limit + date)
                    user_p().takes(book_p())

            user_p.changed()
            book_p.changed()

    def on_entry_loan_changed(self,widget):
        text = widget.get_text().lower().strip()
        self._filter.refilter_loans_text(text)

    def add_edit(self,name,object_p=None):
        fields = dict(editor=['name'],
                      author=['name'],
                      serial=['title'],
                      book=['title','ean','reference','buy_date','serial_nb'],
                      user='firstname lastname student_number mail phone address nb_items year'.split())

        ui = uieditor.UIEditor(os.path.join(os.path.dirname(__file__),'ui/dialog_%s.xml'%name),
                               fields[name],
                               object_p() if object_p else getattr(model,name.title()))

        if name == 'book':
            ui = BookEditor(ui, self._real_models)

        action, obj = ui.run()
        
        if action:
            if action == 'save':
                if object_p:
                    object_p.changed()
                else:
                    self._real_models[name+'s'].append(obj)
            elif action == 'delete':
                assert object_p
                object_p.remove()
                

    def on_tree_editors_row_activated(self,treeview,path,view_column):
        object_p = TreeviewProxy(treeview).get_selected_row()
        self.add_edit('editor',object_p)

    def on_tree_serials_row_activated(self,treeview,path,view_column):
        object_p = TreeviewProxy(treeview).get_selected_row()
        self.add_edit('serial',object_p)

    def on_tree_users_row_activated(self,treeview,path,view_column):
        object_p = TreeviewProxy(treeview).get_selected_row()
        self.add_edit('user',object_p)

    def on_tree_authors_row_activated(self,treeview,path,view_column):
        object_p = TreeviewProxy(treeview).get_selected_row()
        self.add_edit('author',object_p)

    def on_tree_books_row_activated(self,treeview,path,view_column):
        object_p = TreeviewProxy(treeview).get_selected_row()
        self.add_edit('book',object_p)

    def add_editor(self,widget):
        self.add_edit('editor')

    def add_author(self,widget):
        self.add_edit('author')

    def add_serial(self,widget):
        self.add_edit('serial')

    def add_user(self,widget):
        self.add_edit('user')

    def add_book(self,widget):
        self.add_edit('book')

if __name__ == '__main__':
    import os.path

    prefix = os.path.dirname(__file__)
    database.start(os.path.join(prefix,'db.db'))
    ui = UI(os.path.join(prefix,'ui/ui.xml'))
    ui.run()

    ui._w.show_all()
    gtk.main()
