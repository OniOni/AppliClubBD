import gtk

def show_message(message,parent=None):
    dialog = gtk.MessageDialog(parent=parent,flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons=gtk.BUTTONS_OK,message_format=message)
    dialog.connect('response',lambda *args:dialog.destroy())
    dialog.show_all()
    dialog.run()
