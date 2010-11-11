import gtk
import gtk.gdk
import gobject

import generic_tree

class SearchBuffer(object):
    def __init__(self,combo,filter):
        self._buffer = ''
        self._w = gtk.Window(gtk.WINDOW_POPUP)
        self._label = gtk.Entry()
        self._w.add(self._label)

        self._combo = combo

        self._timeout = None
        self._filter = filter
        self._last_search = None

        combo.connect('key-press-event',self._keypress)

    def _keypress(self, widget, event):
        if event.is_modifier:
            return

        if self._timeout:
            gobject.source_remove(self._timeout)

        ctrl = bool(event.state & gtk.gdk.CONTROL_MASK)
        key = gtk.gdk.keyval_name(event.keyval)
        print key
        
        if ctrl and key == 'g':
            if self._last_search:
                self.search()
        else:
            self._last_search = None

            if key == 'BackSpace':
                self._buffer = self._buffer[:-1]
                self.search()
            elif key == 'Escape':
                return self.reset()
            elif len(key) == 1:
                self._buffer += key
                self.search()

            self._label.set_text(self._buffer)
            self.show(bool(self._buffer))

        self._timeout = gobject.timeout_add(2000,self.reset)

       
    def reset(self):
        if self._w.props.visible:
            self._w.hide()
            self._buffer = ''
            return True
        else:
            return False

    def show(self,show):
        if show and not self._w.props.visible:
             self._w.show_all()
             x,y, _, h = self._combo.get_allocation()
             x_w, y_w = self._combo.window.get_origin()

             self._w.move(x+x_w,y+y_w + h )
            
        elif not show:
            self._w.hide()

    def search(self):
        model = self._combo.get_model()

        # we can starts on the Last one selected, but gtk does not
        # like that
        if self._last_search:
            iter = model.iter_next(self._last_search)
        else:
            iter = model.get_iter_first()

        while iter:
            if self._filter(model.get_value(iter,0),self._buffer):
                break

            iter = model.iter_next(iter)

        if iter:
            self._last_search = iter
            self._combo.set_active_iter(iter)


if __name__ == '__main__':
    cb = gtk.ComboBox()
    w = gtk.Window()

    box = gtk.VBox()
    tree1, tree2 = gtk.Image(), gtk.Image()

    w.add(box)
    box.add(tree1)
    
    def filter(obj, key):
        return obj.lower().startswith(key.lower())

    m = generic_tree.Model()
    m.load(sorted(set(open(__file__).read().split())))

    generic_tree.ComboxBoxProxy(cb,str,m)

    buf = SearchBuffer(cb,filter)
    
    box.add(cb)
    box.add(tree2)
    w.show_all()
    
    gtk.main()
