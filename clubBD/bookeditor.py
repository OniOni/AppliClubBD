#coding: utf8
import gtk
from gui.generic_tree import TreeviewProxy, Column, ComboxBoxProxy
from gui.mapper.adapters.gtkAdapters import RadioButtonMapper
from gui.multiple_selection import ChooseModel, ChooseWidget, ChooseModelAdapter

from gui.entry_completion import EntryCompletion

class BookEditor(object):
    def __init__(self, uieditor, models):
        self._uieditor = uieditor
        self._models = models

    def run(self):
        builder = self._uieditor._builder
        model = self._models

        serial = builder.get_object('serial')
        editor = builder.get_object('editor')

        def match_func_name(obj, key):
            return obj.name.lower().startswith(key.lower())

        def match_func_title(obj, key):
            return obj.title.lower().startswith(key.lower())

        def display_func_name(obj):
            return obj.name

        def display_func_title(obj):
            return obj.title

        def search_name(obj, key):
            return key.lower() in obj.name.lower()

        e_editors = EntryCompletion(editor, self._models['editors'], 
                                    display_func_name, match_func_name)
        e_serials = EntryCompletion(serial, self._models['serials'], 
                                    display_func_title, match_func_title)
    
        trees = builder.get_object('have'), builder.get_object('available')

        choose = ChooseModel(model['authors'])
        multiples = ChooseWidget(choose,
                                 (Column("Affectés",str),Column('Disponibles',str)),
                                 trees,
                                 search_name)

        for tree in trees:
            TreeviewProxy(tree).optimise_tree(1)

        def format_prefix(obj):
            if len(obj.prefix) == 1:
                prefix_str, = obj.prefix
            else:
                prefix_str = ', '.join(obj.prefix)

            return "%s - %s"%(obj.title,prefix_str)

        self._uieditor._mapper.update({
                'kind': RadioButtonMapper(
                    {
                        'b': builder.get_object('kind_bd'),
                        'm': builder.get_object('kind_manga'),
                        }
                    ),
                'authors': ChooseModelAdapter(choose),
                'editor':e_editors,
                'serial':e_serials,
                    })

        return self._uieditor.run()
