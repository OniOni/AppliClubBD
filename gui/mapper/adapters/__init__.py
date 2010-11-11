class AutoRegister(type):
    def __init__(self,name,type,dict):
        super(AutoRegister,self).__init__(name,type,dict)
        self._members[self._class] = self
   
class Adapter(object):
    __metaclass__ = AutoRegister
    _members = {}

    _class = None
    
    def __init__(self,widget):
        self._widget = widget
    def get(self):
        raise NotImplementedError
    def set(self,value):
        raise NotImplementedError

def auto_map(properties_widgets):
    mapped = {}

    for prop,widget in properties_widgets.iteritems():
        mapped[prop] = Adapter._members[widget.__class__](widget)
        
    return mapped
